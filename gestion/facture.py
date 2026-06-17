from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from io import BytesIO
from datetime import datetime


def generer_facture(reservation):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    elements = []

    # Titre
    elements.append(Paragraph("FACTURE - GESTION DE CIMETIÈRE", styles['Title']))
    elements.append(Spacer(1, 20))

    # Infos facture
    elements.append(Paragraph(f"Date : {datetime.now().strftime('%d/%m/%Y')}", styles['Normal']))
    elements.append(Paragraph(f"N° Facture : FAC-{reservation.id}-2026", styles['Normal']))
    elements.append(Spacer(1, 20))

    # Infos client
    elements.append(Paragraph("INFORMATIONS CLIENT", styles['Heading2']))
    elements.append(Paragraph(f"Nom : {reservation.client.get_full_name() or reservation.client.username}", styles['Normal']))
    elements.append(Spacer(1, 20))

    # Infos caveau
    elements.append(Paragraph("DÉTAILS DE LA RÉSERVATION", styles['Heading2']))
    data = [
        ['Description', 'Détails'],
        ['Caveau N°', reservation.caveau.numero],
        ['Section', reservation.caveau.section],
        ['Bloc', reservation.caveau.bloc],
        ['Défunt', f"{reservation.defunt.prenom} {reservation.defunt.nom}" if reservation.defunt else 'N/A'],
        ['Statut', reservation.statut],
    ]

    table = Table(data, colWidths=[200, 250])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
    ]))
    elements.append(table)
    elements.append(Spacer(1, 30))

    # Montant
    elements.append(Paragraph("MONTANT TOTAL : 150 USD", styles['Heading2']))
    elements.append(Spacer(1, 20))
    elements.append(Paragraph("Merci pour votre confiance.", styles['Normal']))

    doc.build(elements)
    buffer.seek(0)
    return buffer