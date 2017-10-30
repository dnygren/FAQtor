###########################################################################
# GNUMakefile $Revision: 1.3 $ : Automate building FAQs using faqtor.py
# Release $Name:  $ (Only defined if checked out as a specific release)
#
# by Daniel C. Nygren $Date: 2017/10/30 22:17:09 $
# Permanent E-mail: dan.nygren@alumni.clemson.edu
#
# Copyright 2017 by Daniel C. Nygren
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation; either version 2 of the License, or (at your option) any later
# version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, contact the Free Software Foundation, Inc., via
# e-mail: info@fsf.org or their website: https://www.fsf.org/about/contact/ .
#
# FAQ.html is created from the source files FAQ.xml and FAQ.cfg using the Python
# script faqtor.py in a subdirectory I've named FAQ.
#
# Then we copy FAQ.html out of the FAQ subdirectory into the parent directory
# where all the other readable files for the web page are kept while preserving
# the permissions it was set with so we don't have the problem of unreadable
# web pages occurring after every update to the FAQ.
#
# CALLING SEQUENCE      gmake  [target] [RELEASE=RCS_MARK_SYMBOL]
#
# EXAMPLES              gmake 
#                       gmake dist  (Creates .zip and .tar.gz distribution files)
#
# TARGET SYSTEM         Any
#
# DEVELOPMENT SYSTEM    Solaris 10
#
# CALLS                 faqtor.py, FAQ.xml, FAQ.cfg, rlog, grep, cut, zip, tar,
#			gzip, chmod, cp, rm
#
# CALLED BY             N/A
#
# INPUTS                N/A
#
# OUTPUTS               FAQ.html
#
# RETURNS               N/A
#
# ERROR HANDLING        If there is an error in a rule, make gives up on the current rule
#
# WARNINGS              Invoke GNU make, not Solaris make or any other make version.
#
###########################################################################
###########################################################################
#               REVISIONS
#
# $Log: GNUmakefile,v $
# Revision 1.3  2017/10/30 22:17:09  dnygren
# Cleanup for github submission
#
# Revision 1.2  2011/05/06 16:55:47  nygren
# Added a make dist option to create .zip and .tar.gz distribution files.
#
# Revision 1.1  2010/09/17 19:25:13  nygren
# Initial revision
#
###########################################################################

# Mask that the target file will be set to
FMASK = u=rw,g=r,o=r

FAQ.html : FAQ.xml FAQ.cfg
	faqtor.py FAQ.xml FAQ.cfg
	-chmod $(FMASK) $@
	cp -p $@ ..


# *** Rules ****

# *** Phony Rules ****

# ### Rule to create a distribution file from the directory tree ###
# The "-" at the beginning of the command tells GNU make ignore errors like
# file not present etc.
.PHONY: dist

# Find the FAQtor version
FAQTOR_VERSION = $(shell rlog faqtor.py | grep 'head:' | cut -d' ' -f2)

dist :
	-rm *.tar.gz *.zip
	 zip -r FAQtor_$(FAQTOR_VERSION).zip . -i faqtor.py README* FAQ* GNUmakefile LICENSE.txt
	-tar -cvf FAQtor_$(FAQTOR_VERSION).tar --exclude-from tar_exclude_file.txt .
	 gzip FAQtor_$(FAQTOR_VERSION).tar
	-chmod $(FMASK)  FAQtor_$(FAQTOR_VERSION).zip
	-chmod $(FMASK) FAQtor_$(FAQTOR_VERSION).tar.gz
