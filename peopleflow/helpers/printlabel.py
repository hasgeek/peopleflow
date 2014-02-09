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


def printlabel(printer, print_type, lines, options={}):

    f = tempfile.NamedTemporaryFile(suffix='.pdf', delete=False)
    fname = f.name
    f.close()
    if 'label' in options and options['label']:
        lines.append(options['label'].upper())
    if print_type == 'label':
        heights = [18, 32, 38, 47]

        doc = SimpleDocTemplate(fname,
                                pagesize=(62 * mm, heights[len(lines) - 1] * mm),
                                topMargin=0, leftMargin=0,
                                rightMargin=0, bottomMargin=0)
        styles = [
        ParagraphStyle("s1", fontName="Helvetica-Bold", alignment=TA_CENTER, fontSize=15, leading=15),
        ParagraphStyle("s2", fontName="Helvetica", alignment=TA_CENTER, fontSize=15, leading=18, spaceBefore=4),
        ParagraphStyle("s3", fontName="Helvetica", alignment=TA_CENTER, fontSize=12, leading=13, spaceBefore=4),
        ParagraphStyle("s4", fontName="Helvetica-Bold", alignment=TA_CENTER, fontSize=20, leading=22, textColor="#444444"),
        ]
        name_len = 1
    else:
        doc = SimpleDocTemplate(fname,
                                pagesize=(95 * mm, 134 * mm),
                                topMargin=(60 if 'topMargin' not in options else options['topMargin']) * mm,
                                leftMargin=(1 if 'leftMargin' not in options else options['leftMargin']) * mm,
                                rightMargin=(1 if 'rightMargin' not in options else options['rightMargin']) * mm,
                                bottomMargin=(9 if 'bottomMargin' not in options else options['bottomMargin']) * mm)
        name = lines[0].strip().upper().split(" ")
        lines = [name[0], " ".join(name[1:]) if len(name[1:]) else None] + lines[1:]
        styles = [
        ParagraphStyle("s1", fontName="Helvetica-Bold", alignment=TA_CENTER, fontSize=40 if len(name[0]) < 9 else 30 if len(name[0]) < 11 else 25, leading=40 if len(name[0]) < 9 else 30 if len(name[0]) < 11 else 25, textColor=options['name_color'] if 'name_color' in options and options['name_color'] else "#000000"),
        ParagraphStyle("s2", fontName="Helvetica-Bold", alignment=TA_CENTER, fontSize=20, leading=22, textColor=options['name_color'] if 'name_color' in options and options['name_color'] else "#000000"),
        ParagraphStyle("s3", fontName="Helvetica-Bold", alignment=TA_CENTER, fontSize=17, leading=19, spaceBefore=2, textColor=options['company_color'] if 'company_color' in options and options['company_color'] else "#000000"),
        ParagraphStyle("s4", fontName="Helvetica-Bold", alignment=TA_CENTER, fontSize=20, leading=27, spaceBefore=2, textColor=options['twitter_color'] if 'twitter_color' in options and options['twitter_color'] else "#55ACEE"),
        ParagraphStyle("s5", fontName="Helvetica-Bold", alignment=TA_CENTER, fontSize=22, leading=30, textColor="#444444"),
        ]
        name_len = 2
    story = []

    for i, line in enumerate(lines):
        if i < len(styles):
            if line:
                story.append(Paragraph(line, styles[i]))
            if i == name_len - 1 and len(lines) > name_len:
                story.append(HRFlowable(width='95%', spaceBefore=5, thickness=2, color=options['hr_color'] if 'hr_color' in options and options['hr_color'] else "#777777"))
    if 'label' in options and options['label']:
        story = story[-1:] + story[:-1]
    doc.build(story)

    os.system("lpr -o page-ranges=1 -P %s %s" % (printer, fname))
    time.sleep(2)
    os.unlink(fname)

def make_label_content(participant):
    data = [participant.name]
    if participant.company:
        compline = participant.company
        if participant.job:
            compline = u"%s, %s" % (participant.job, compline)
        data.append(compline)
    else:
        data.append(None)
    if participant.twitter:
        data.append('@' + participant.twitter)
    else:
        data.append(None)
    return data


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Script to test printing of labels. Tries to test through fairly large 2-liners for name and job+company.')
    parser.add_argument('printer', type=str, help='The name of the printer')
    parser.add_argument('--lines', type=int, help='The number of lines to print', default=3)
    parser.add_argument('--type', type=str, help='Print type. Either label or badge', default='label')
    args = parser.parse_args()
    data = ["Kiran Jonnalagadda isn't long enough", "CEO, HasGeek Media LLP.", "@jackerhack", "CREW"]
    data = data[:args.lines]
    printlabel(args.printer, args.type, data)
