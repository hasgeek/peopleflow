#!/usr/bin/env python

import tempfile
import argparse
import os, time
from reportlab.lib.units import mm
from reportlab.lib.enums import TA_CENTER
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.platypus.flowables import HRFlowable
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.colors import Color


def printlabel(printer, lines):

    f = tempfile.NamedTemporaryFile(suffix='.pdf', delete=False)
    fname = f.name
    f.close()

    heights = [18, 32, 38, 47]

    doc = SimpleDocTemplate(fname,
                            pagesize=(62 * mm, heights[len(lines) - 1] * mm),
                            topMargin=0, leftMargin=0,
                            rightMargin=0, bottomMargin=0)
    story = []

    styles = [
        ParagraphStyle("s1", fontName="Helvetica-Bold", alignment=TA_CENTER, fontSize=15, leading=15),
        ParagraphStyle("s2", fontName="Helvetica", alignment=TA_CENTER, fontSize=15, leading=18, spaceBefore=4),
        ParagraphStyle("s3", fontName="Helvetica", alignment=TA_CENTER, fontSize=12, leading=13, spaceBefore=4),
        ParagraphStyle("s4", fontName="Helvetica-Bold", alignment=TA_CENTER, fontSize=20, leading=22, textColor="#444444"),
        ]
    for i, line in enumerate(lines):
        if i < len(styles):
            story.append(Paragraph(line, styles[i]))
            if i == 0 and len(lines) > 1:
                story.append(HRFlowable(width='95%', spaceBefore=5))
    if lines[len(lines) - 1] == "CREW":
        story = story[-1:] + story[:-1]
    doc.build(story)

    os.system("lpr -P %s %s" % (printer, fname))
    time.sleep(2)
    os.unlink(fname)

def make_label_content(participant):
    data = [participant.name]
    if participant.company:
        compline = participant.company
        if participant.job:
            compline = u"%s, %s" % (participant.job, compline)
        data.append(compline)
    if(participant.twitter):
        data.append('@' + participant.twitter)
    if u'Crew' in participant.purchases:
        data.append("CREW")
    return data


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Script to test printing of labels. Tries to test through fairly large 2-liners for name and job+company.')
    parser.add_argument('printer', type=str, help='The name of the printer')
    parser.add_argument('--lines', type=int, help='The number of lines to print', default=3)
    args = parser.parse_args()
    data = ["Kiran Jonnalagadda isn't long enough", "CEO, HasGeek Media LLP.", "@jackerhack", "CREW"]
    data = data[:args.lines]
    printlabel(args.printer, data)
