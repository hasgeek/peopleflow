#!/usr/bin/env python

import tempfile
import os, time
from reportlab.lib.units import mm
from reportlab.lib.enums import TA_CENTER
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import ParagraphStyle


def printlabel(line1, line2=''):

    f = tempfile.NamedTemporaryFile(suffix='.pdf', delete=False)
    fname = f.name
    f.close()

    doc = SimpleDocTemplate(fname,
                            pagesize=(62 * mm, 30 * mm),
                            topMargin=0, leftMargin=0,
                            rightMargin=0, bottomMargin=0)
    story = []

    style1 = ParagraphStyle("s1", fontName="Helvetica", alignment=TA_CENTER, fontSize=18, leading=18)
    style2 = ParagraphStyle("s2", fontName="Helvetica", alignment=TA_CENTER, fontSize=13, leading=13, spaceBefore=6)

    story.append(Paragraph(line1, style1))
    story.append(Paragraph(line2, style2))
    doc.build(story)

    #os.system("gnome-open " + fname)
    os.system("lpr -P Brother-QL-570 " + fname)
    time.sleep(2)
    os.unlink(fname)


if __name__ == '__main__':
    printlabel("Kiran Jonnalagadda isn't long enough", "@jackerhack")
