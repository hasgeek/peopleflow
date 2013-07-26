#!/usr/bin/env python

import tempfile
import argparse
import os, time
from reportlab.lib.units import mm
from reportlab.lib.enums import TA_CENTER
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import ParagraphStyle


def printlabel(printer, lines):

    f = tempfile.NamedTemporaryFile(suffix='.pdf', delete=False)
    fname = f.name
    f.close()

    doc = SimpleDocTemplate(fname,
                            pagesize=(62 * mm, 40 * mm),
                            topMargin=0, leftMargin=0,
                            rightMargin=0, bottomMargin=0)
    story = []

    styles = [
        ParagraphStyle("s1", fontName="Helvetica", alignment=TA_CENTER, fontSize=18, leading=18),
        ParagraphStyle("s2", fontName="Helvetica", alignment=TA_CENTER, fontSize=13, leading=13, spaceBefore=6),
        ParagraphStyle("s3", fontName="Helvetica", alignment=TA_CENTER, fontSize=13, leading=13, spaceBefore=6),
        ParagraphStyle("s4", fontName="Helvetica", alignment=TA_CENTER, fontSize=13, leading=13, spaceBefore=6)
        ]

    for i, line in enumerate(lines):
        story.append(Paragraph(line, styles[i]))
    # story.append(Paragraph(line2, style2))
    doc.build(story)

    #os.system("gnome-open " + fname)
    os.system("lpr -P %s %s" % (printer, fname))
    time.sleep(2)
    os.unlink(fname)

def make_label_content(participant):
    data = [participant.name]
    if participant.company:
        data.append(participant.company)
        if participant.job:
            data.append(participant.job)
    if(participant.twitter):
        data.append('@' + participant.twitter)
    return data


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Script to print labels')
    parser.add_argument('printer', type=str, help='The name of the printer')
    args = parser.parse_args()
    printlabel(args.printer, ["Kiran Jonnalagadda isn't long enough", "@jackerhack"])
