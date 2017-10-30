#!/bin/env python
import sys, os, re
import time
from time import strftime
from xml.sax import saxutils, handler, make_parser, parseString
from xml.sax.handler import feature_namespaces
try:
   from ConfigParser import RawConfigParser as ConfigParser
except:
   print "FAQtor requires python >= 2.3"
   sys.exit(1)


FILENAME_RX = re.compile("filename\s*[=:]\s*(?P<filename>.*)")
MULTILINE_RX = re.compile(r"\\\n")

HTML_LEFT_TAG_RX = re.compile(r"<(?!/?(faq|section|answer|question))(?=.*?>)")
HTML_RIGHT_TAG_RX = re.compile(r"(&lt;.*?)(>)")

DEFAULTS = {
    'format_section': ' <h1>%(section)s</h1>',
    'format_question':  "Q. %(sindex)s.%(qindex)s &nbsp; %(question)s<br>",
    'format_answer': '<p align="right">A. %(sindex)s.%(qindex)s</p>' +
                     '<h2>%(question)s</h2><br>%(answer)s',
    'format_top': '<p align="right">Return to top</p>',
    'page_start': '<center><h1>Frequently Asked Questions</h1></center>',
    'page_end': '</body></html>',
    'page_sep': '<hr>',
    'output_filename': 'faq.html',
    'index_start': '<table border="0">',
    'index_end': '</table>',
    'index_section': '<tr><th colspan="2" align="left">&nbsp;<br>%(section)s</th></tr>',
    'index_question': '<tr><td>Q.&nbsp;%(sindex)s.%(qindex)s&nbsp;</td>' +
                               '<td valign="top">%(question)s</td></tr>'
    }

class InputReader(handler.ContentHandler):
   def __init__(self):
      self.section_names = []
      #self.answer_names = {}  # maps "section#_answer#" to answer name
      self.sections = {}
      self.section = None
      self.key = None
      self.data = ""
      self.question = ""
      self.answer = ""
      self.answer_name = None
      
   def getNumSections(self):
      return len(self.section_names)

   def getSectionName(self, sectionNum):
      if sectionNum >= len(self.section_names):
         return None

      return self.section_names[sectionNum]

   def getSectionQandA(self, sectionName):
      if not self.sections.has_key(sectionName):
         return None

      return self.sections[sectionName]

   def __iter__(self):
      self.start = 0
      return self

   def next(self):
      section = self.getSectionName(self.start)
      if section == None:
         raise StopIteration
      q, a, aname = self.getSectionQandA(section)
      self.start += 1
      return self.start, section, q, a, aname

    
   def getData(self):
      print self.section_names
      print
      print self.sections

        
   def startElement(self, name, attrs):
      name = name.lower()
      self.key = name
      if name == 'section':
         self.section = attrs.get('name')
         self.section_names.append(self.section)
         self.sections[self.section] = ([], [], []) # questions, answers, answer_names
      elif name == 'question':
         self.question = ""
      elif name == 'answer':
         self.answer_name = attrs.get('name')
         self.answer = ""


   def endElement(self, name):
      name = name.lower()
      if name == 'question':
         self.question = self.data
      elif name == 'answer':
         self.answer = self.data
         self.sections[self.section][0].append(self.question.lstrip())
         self.sections[self.section][1].append(self.answer.lstrip())
         self.sections[self.section][2].append(self.answer_name)
      self.data = ""
      self.answer_name = None
          
   def characters(self, content):
      self.data += content

        
class FAQtor:
    def __init__(self, xmlfile, configfile):
        self.opts = {}
        self.read_config(configfile)
        self.read_input(xmlfile)


    def read_config(self, configfile):
        if configfile:
            try:
                fp = open(configfile, "r")
            except Exception, e:
                print "error reading config file:", configfile
                print e
                sys.exit(1)

            config = ConfigParser()
            config.readfp(fp)
            fp.close()
        
            for s in config.sections():
               for o in config.options(s):
                  val = config.get(s,o).strip()
                  val = MULTILINE_RX.sub('\n', val)
                  self.opts["%s_%s" % (s, o)] = val

        # replace any missing config opts w/ defaults
        for k,v in DEFAULTS.items():
            self.opts.setdefault(k, v)


    def replace_markup(self, data):
        data = HTML_LEFT_TAG_RX.sub("&lt;", data)
        while 1:
           m = HTML_RIGHT_TAG_RX.search(data)
           if not m: break
           after = data[m.end():]
           before = data[:m.end()-1]
           data = "%s&gt;%s" % (before, after)
           
        return data


    def read_input(self, xmlfile):
        try:
            fp = open(xmlfile, "r")
        except Exception, e:
            print "error reading input file:", xmlfile
            print e
            sys.exit(1)

        data = self.replace_markup(fp.read())
        fp.close()

	#print data
        # Create the handler
        ir = InputReader()
        
        # Parse the xml string, data with xml reader, ir
        # print data
        parser = parseString(data, ir)
        
        fp = open(self.opts['output_filename'], "w")
        fp.write("<!-- This page was generated automatically with FAQtor.py -->\n\n")
        fp.write('<a name="#top"></a>\n')

        self.output_page_start(fp)
        fp.write("<center><h3>Last updated: %s </h3></center>\n\n" % strftime("%d %b %Y") )
        
        # display the questions within each section
        fp.write("%s\n" % self.opts['index_start'])
        for sectionnum, section, questions, answers, answer_names in ir:
            self.output_index_section(fp, section)
            self.output_index_questions(fp, sectionnum, questions)
        fp.write("%s\n" % self.opts['index_end'])


        fp.write("%s\n" % self.opts['page_sep'])
        # display the questions and answers within each section
        for sectionnum, section, questions, answers, answer_names in ir:
            self.output_section(fp, section)
            self.output_questions_and_answers(fp,
                                              sectionnum,
                                              questions,
                                              answers,
                                              answer_names)
        self.output_page_end(fp)
        fp.close()


    def output_page_start(self, fp):
        self.__output_page_part(fp, self.opts['page_start'])

    def output_page_end(self, fp):
        self.__output_page_part(fp, self.opts['page_end'])

    def __output_page_part(self, fp, param):
        param=param.strip()
        m = FILENAME_RX.match(param)
        if m:
            filename = m.group('filename')
            try:
                f = open(filename, "r")
                for l in f:
                    fp.write("%s" % l)
                f.close()
            except Exception, e:
                print "Could not read input file:", filename
                print e
                sys.exit(0)
        else:
            fp.write("%s\n" % param)

    def output_index_section(self, fp, section):
        fp.write("%s\n" % (self.opts['index_section'] % {'section': section}))


    def output_section(self, fp, section):
        fp.write("%s\n" % (self.opts['format_section'] % {'section': section}))


    def output_index_questions(self, fp, snum, questions):
        i = 0
        d = {'sindex': snum}
        d.update(self.opts)
        for q in questions:
            question = '<a href="#%d_%d">%s</a>' % (snum,i,q)
            d['qindex'] = i
            d['question'] = question

            #s = self.opts['format_question'] % d

            fp.write('%s\n' % self.opts['index_question'] % d)
            i += 1

    def output_questions_and_answers(self, fp, snum, questions, answers, answer_names):
        l = len(questions)
        d = {'sindex': snum}
        d.update(self.opts)
        for i in range(l):
            #question = '<a name="%d_%d"></a>%s\n' % (snum, i, questions[i])
            
            d['question'] = questions[i]
            d['answer'] = answers[i]
            d['aindex'] = i
            d['qindex'] = i

            if (answer_names[i] != None):
               fp.write('<a name="%s"></a>\n' % answer_names[i])
                        
            fp.write('<a name="%d_%d"></a>\n' % (snum, i))
            fp.write('%s\n' % self.opts['format_answer'] % d)

            top = '<a href="#top">%s</a>' % self.opts['format_top'] % d
            fp.write('%s\n' % top)
            fp.write('%s\n' % self.opts['page_sep'])

        

if __name__ == '__main__':
    args = sys.argv
    if len(args) not in (2,3):
        print "You must supply an input file and a config file"
        print "Usage:   faqtor.py  inputfile  [configfile]"
        sys.exit(1)

    inputfile = args[1]
    if len(args) == 3: configfile = args[2]
    else: configfile = None
    faqtor = FAQtor(inputfile, configfile)


    
        
