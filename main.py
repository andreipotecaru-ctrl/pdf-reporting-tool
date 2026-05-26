import eel
import os
import tkinter as tk
from tkinter import filedialog
import pandas as pd
from reportlab.lib.pagesizes import A4, letter, legal, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.pdfencrypt import StandardEncryption

eel.init('web')


@eel.expose
def selecteaza_fisier_local():
    root = tk.Tk()
    root.withdraw()
    root.wm_attributes('-topmost', 1)
    cale_fisier = filedialog.askopenfilenames(
        title="Select Data File(s)",
        filetypes=[("Data Files", "*.xlsx *.xls *.csv")]
    )
    root.destroy()
    return list(cale_fisier) if cale_fisier else []


def genereaza_structura_pdf(cale_director_iesire, nume_pdf_final, df, dimensiune_pagina, orientare_pagina, date_antet,
                            date_subsol):
    dimensiuni = {"A4": A4, "LETTER": letter, "LEGAL": legal}
    format_ales = dimensiuni.get(dimensiune_pagina.upper(), A4)
    if orientare_pagina.lower() == "peisaj":
        format_ales = landscape(format_ales)

    if not os.path.exists(cale_director_iesire):
        os.makedirs(cale_director_iesire)

    cale_iesire = os.path.join(cale_director_iesire, f"{nume_pdf_final}.pdf")

    setari_criptare = None
    cnp_complet = str(date_antet.get('cnp', '')).strip()

    if date_antet.get('paroleaza_pdf', True) and len(cnp_complet) >= 6:
        parola_pdf = cnp_complet[-6:]
        setari_criptare = StandardEncryption(userPassword=parola_pdf, canPrint=1, canModify=0)

    doc = SimpleDocTemplate(
        cale_iesire,
        pagesize=format_ales,
        leftMargin=20, rightMargin=20, topMargin=20, bottomMargin=20,
        encrypt=setari_criptare,
        pageCompression=1
    )

    doc.title = nume_pdf_final
    doc.author = "System"
    doc.subject = "Activity Report"
    doc.creator = "Application"

    stiluri = getSampleStyleSheet()
    stil_titlu_brand = ParagraphStyle('BTitle', fontName='Helvetica-Bold', fontSize=26, leading=30,
                                      textColor=colors.HexColor("#E74C3C"), alignment=1, spaceAfter=15)
    stil_meta = ParagraphStyle('MText', fontName='Helvetica', fontSize=9, leading=13,
                               textColor=colors.HexColor("#1A252F"))
    stil_intro = ParagraphStyle('IText', fontName='Helvetica', fontSize=8.5, leading=13,
                                textColor=colors.HexColor("#34495E"), spaceBefore=10, spaceAfter=15, alignment=4)
    stil_subsol = ParagraphStyle('SText', fontName='Helvetica', fontSize=8.5, leading=12,
                                 textColor=colors.HexColor("#2C3E50"), spaceBefore=20, spaceAfter=5, alignment=1)
    stil_copy = ParagraphStyle('CText', fontName='Helvetica-Bold', fontSize=8, alignment=2)

    elemente = []

    if date_antet.get('companie'):
        elemente.append(Paragraph(date_antet['companie'].upper(), stil_titlu_brand))

    date_client = [
        [Paragraph("<b>Name:</b>", stil_meta), Paragraph(date_antet.get('nume', ''), stil_meta)],
        [Paragraph("<b>ID/Tax Code:</b>", stil_meta), Paragraph(date_antet.get('cnp', ''), stil_meta)],
        [Paragraph("<b>E-mail:</b>", stil_meta),
         Paragraph(f"<font color='#3498db'>{date_antet.get('email', '')}</font>", stil_meta)]
    ]
    tabel_client = Table(date_client, colWidths=[80, 420])
    tabel_client.setStyle(TableStyle([('VALIGN', (0, 0), (-1, -1), 'TOP'), ('BOTTOMPADDING', (0, 0), (-1, -1), 1),
                                      ('TOPPADDING', (0, 0), (-1, -1), 1)]))
    elemente.append(tabel_client)

    if date_antet.get('text_intro'):
        elemente.append(Paragraph(date_antet['text_intro'], stil_intro))

    df_print = df.drop(columns=['_AnLunaTmp'], errors='ignore')
    date_pdf = [[str(col) for col in df_print.columns]]
    for rand in df_print.values:
        date_pdf.append([str(celula) if pd.notna(celula) else "" for celula in rand])

    tabel_date = Table(date_pdf, repeatRows=1)

    font_size = 6 if orientare_pagina.lower() == "peisaj" else 4.5
    if len(df_print.columns) <= 8:
        font_size += 1

    tabel_date.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#111827")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), font_size),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 4),
        ('TOPPADDING', (0, 0), (-1, 0), 4),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor("#FFFFFF")),
        ('GRID', (0, 0), (-1, -1), 0.4, colors.HexColor("#BDC3C7")),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), font_size - 0.5),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    elemente.append(tabel_date)

    if date_subsol.get('text_declaratie'):
        elemente.append(Paragraph(date_subsol['text_declaratie'], stil_subsol))
    if date_subsol.get('text_copyright'):
        elemente.append(Paragraph(date_subsol['text_copyright'], stil_copy))

    doc.build(elemente)

    try:
        import subprocess
        ps_command = f'icacls "{cale_iesire}" /reset'
        subprocess.run(ps_command, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception:
        pass

    return cale_iesire


def citeste_si_filtreaza(cale_fisier, coloane_tinta):
    extensie = os.path.splitext(cale_fisier)[1].lower()
    if extensie == '.csv':
        for enc in ['utf-8', 'cp1252', 'latin1', 'utf-8-sig']:
            try:
                return pd.read_csv(cale_fisier, usecols=coloane_tinta, encoding=enc)
            except (UnicodeDecodeError, ValueError):
                continue
    else:
        return pd.read_excel(cale_fisier, usecols=coloane_tinta)
    return None


@eel.expose
def proceseaza_tab_transactions(cale_fisier, dimensiune_pagina, orientare_pagina, date_antet, date_subsol,
                                export_luni_separat):
    try:
        coloane = ["Reference ID", "Date & Time", "Reason", "Bet Type", "Game Name", "Game ID", "Game Provider",
                   "Payment Method", "Account Type", "Currency", "Amount", "Balance"]
        eel.actualizeazaStatus("Loading Account Transactions data...")()
        df = citeste_si_filtreaza(cale_fisier, coloane)
        if df is None: return {"succes": False, "eroare": "Invalid format or missing required columns!"}

        df = df[coloane]
        cale_folder_export = os.path.join(os.getcwd(), "PDF_Reports_Export")
        brand = date_antet.get('companie', 'PLATFORM')
        nume_client = date_antet.get('nume', 'Client')

        luni_en = {1: "January", 2: "February", 3: "March", 4: "April", 5: "May", 6: "June",
                   7: "July", 8: "August", 9: "September", 10: "October", 11: "November", 12: "December"}

        if export_luni_separat:
            eel.actualizeazaStatus("Parsing timestamps and grouping data by month...")()
            df['_DataParsed'] = pd.to_datetime(df['Date & Time'], format='%d/%m/%Y %H:%M:%S', errors='coerce')
            df = df.dropna(subset=['_DataParsed'])
            df['_AnLunaTmp'] = df['_DataParsed'].dt.to_period('M')
            grupuri = df.groupby('_AnLunaTmp')

            fisiere_generate = []

            for perioada, grup in grupuri:
                an = perioada.year
                luna_numar = perioada.month
                nume_luna_en = luni_en.get(luna_numar, f"month_{luna_numar}")

                nume_pdf = f"Activity_History_{brand}_[{nume_luna_en}_{an}]_-_{nume_client}"

                eel.actualizeazaStatus(f"Generating PDF: {nume_pdf}...")()
                grup_curat = grup.drop(columns=['_DataParsed']).head(5000)

                cale = genereaza_structura_pdf(cale_folder_export, nume_pdf, grup_curat, dimensiune_pagina,
                                               orientare_pagina, date_antet, date_subsol)
                fisiere_generate.append(os.path.basename(cale))

            return {"succes": True, "multiple": True, "fisiere": fisiere_generate}

        else:
            nume_pdf = f"Activity_History_{brand}_-_{nume_client}"
            df = df.head(5000)
            cale = genereaza_structura_pdf(cale_folder_export, nume_pdf, df, dimensiune_pagina, orientare_pagina,
                                           date_antet, date_subsol)
            return {"succes": True, "multiple": False, "cale": os.path.basename(cale)}

    except Exception as e:
        return {"succes": False, "eroare": str(e)}


@eel.expose
def proceseaza_tab_financial(cale_fisier, dimensiune_pagina, orientare_pagina, date_antet, date_subsol):
    try:
        coloane = ["Creation Date", "Latest Update", "Username", "Status", "Transfer ID", "Account Details",
                   "Payment Method", "Action Type", "Amount", "Currency", "Tax Amount", "Amount before tax"]
        eel.actualizeazaStatus("Loading Financial Transactions data...")()
        df = citeste_si_filtreaza(cale_fisier, coloane)
        if df is None: return {"succes": False, "eroare": "Invalid format or missing required columns!"}

        df = df[coloane].head(5000)
        cale_folder_export = os.path.join(os.getcwd(), "PDF_Reports_Export")
        brand = date_antet.get('companie', 'PLATFORM')
        nume_client = date_antet.get('nume', 'Client')

        nume_pdf = f"Financial_Transactions_{brand}_-_{nume_client}"

        cale = genereaza_structura_pdf(cale_folder_export, nume_pdf, df, dimensiune_pagina, orientare_pagina,
                                       date_antet, date_subsol)
        return {"succes": True, "multiple": False, "cale": os.path.basename(cale)}
    except Exception as e:
        return {"succes": False, "eroare": str(e)}


@eel.expose
def proceseaza_tab_logins(cale_fisier, dimensiune_pagina, orientare_pagina, date_antet, date_subsol):
    try:
        coloane_sursa = [
            "Login Time", "Logout Time", "Username", "User Email",
            "First Name", "Last Name", "Login Ip", "IP Country Code", "Client Type"
        ]

        eel.actualizeazaStatus("Loading Login History data...")()

        if cale_fisier.endswith('.csv'):
            df_header = pd.read_csv(cale_fisier, nrows=1)
        else:
            df_header = pd.read_excel(cale_fisier, nrows=1)

        redenumiri = {col: str(col).strip() for col in df_header.columns}
        for col in df_header.columns:
            if str(col).strip().lower() == "logout tim":
                redenumiri[col] = "Logout Time"

        if cale_fisier.endswith('.csv'):
            df = pd.read_csv(cale_fisier)
        else:
            df = pd.read_excel(cale_fisier)

        df = df.rename(columns=redenumiri)
        toate_existe = all(c in df.columns for c in coloane_sursa)

        if not toate_existe:
            return {
                "succes": False,
                "eroare": f"Invalid format! Required columns missing.\nExpected: {coloane_sursa}"
            }

        df_final = df[coloane_sursa].head(5000)
        cale_folder_export = os.path.join(os.getcwd(), "PDF_Reports_Export")
        brand = date_antet.get('companie', 'PLATFORM')
        nume_client = date_antet.get('nume', 'Client')

        nume_pdf = f"Login_History_{brand}_-_{nume_client}"

        cale = genereaza_structura_pdf(cale_folder_export, nume_pdf, df_final, dimensiune_pagina, orientare_pagina,
                                       date_antet, date_subsol)
        return {"succes": True, "multiple": False, "cale": os.path.basename(cale)}
    except Exception as e:
        return {"succes": False, "eroare": str(e)}


@eel.expose
def proceseaza_tab_communications(cale_fisier, dimensiune_pagina, orientare_pagina, date_antet, date_subsol):
    try:
        coloane = ["SentDate", "Channel", "Subject", "Status"]
        eel.actualizeazaStatus("Loading Communications data...")()
        df = citeste_si_filtreaza(cale_fisier, coloane)
        if df is None: return {"succes": False, "eroare": "Invalid format or missing required columns!"}

        df = df[coloane]
        df = df[df['Channel'].str.strip().isin(['E-mail', 'SMS'])]
        df = df.head(5000)

        cale_folder_export = os.path.join(os.getcwd(), "PDF_Reports_Export")
        brand = date_antet.get('companie', 'PLATFORM')
        nume_client = date_antet.get('nume', 'Client')

        nume_pdf = f"Communications_History_{brand}_-_{nume_client}"

        cale = genereaza_structura_pdf(cale_folder_export, nume_pdf, df, dimensiune_pagina, orientare_pagina,
                                       date_antet, date_subsol)
        return {"succes": True, "multiple": False, "cale": os.path.basename(cale)}
    except Exception as e:
        return {"succes": False, "eroare": str(e)}


@eel.expose
def proceseaza_tab_bonus(fisiere_selectate, dimensiune_pagina, orientare_pagina, date_antet, date_subsol):
    try:
        if not fisiere_selectate:
            return {"succes": False, "eroare": "No files selected for consolidation!"}

        toate_coloanele_posibile = [
            "bonusName", "bonusStatus", "activationDate", "bonusGivenDate", "bonusVertical",
            "Bonus Name", "Status", "Activation Date", "Given Date", "Vertical", "Type", "Amount"
        ]

        dictionar_redenumire = {
            "bonusName": "Bonus Name",
            "bonusStatus": "Status",
            "activationDate": "Activation Date",
            "bonusGivenDate": "Given Date",
            "bonusVertical": "Vertical"
        }

        liste_df = []
        coloane_detectate = None

        for cale_fisier in fisiere_selectate:
            eel.actualizeazaStatus(f"Analyzing file structure: {os.path.basename(cale_fisier)}")()

            if cale_fisier.endswith('.csv'):
                df_header = pd.read_csv(cale_fisier, nrows=1)
            else:
                df_header = pd.read_excel(cale_fisier, nrows=1)

            coloane_gasite = [col for col in toate_coloanele_posibile if col in df_header.columns]

            if not coloane_gasite:
                continue

            if coloane_detectate is None:
                coloane_detectate = coloane_gasite

            df_partial = citeste_si_filtreaza(cale_fisier, coloane_detectate)
            if df_partial is not None:
                liste_df.append(df_partial)

        if not liste_df:
            return {"succes": False,
                    "eroare": "None of the selected files contain valid bonus data columns (legacy or modern format)!"}

        eel.actualizeazaStatus("Merging files and formatting table structures...")()

        df_final = pd.concat(liste_df, ignore_index=True)
        df_final = df_final[coloane_detectate].head(5000)

        df_final = df_final.rename(columns=dictionar_redenumire)

        cale_folder_export = os.path.join(os.getcwd(), "PDF_Reports_Export")
        brand = date_antet.get('companie', 'PLATFORM')
        nume_client = date_antet.get('nume', 'Client')

        nume_pdf = f"Consolidated_Bonus_History_{brand}_-_{nume_client}"

        cale = genereaza_structura_pdf(cale_folder_export, nume_pdf, df_final, dimensiune_pagina, orientare_pagina,
                                       date_antet, date_subsol)
        return {"succes": True, "multiple": False, "cale": os.path.basename(cale)}

    except Exception as e:
        return {"succes": False, "eroare": str(e)}


@eel.expose
def proceseaza_tab_se_history(cale_fisier, dimensiune_pagina, orientare_pagina, date_antet, date_subsol):
    try:
        coloane_tinta = ["Vertical", "Type", "Start Date", "End Date", "Created on", "Created by", "Updated on",
                         "Status"]

        eel.actualizeazaStatus("Loading Self Exclusion History data...")()
        df = citeste_si_filtreaza(cale_fisier, coloane_tinta)
        if df is None:
            return {"succes": False,
                    "eroare": "Invalid format or missing columns! Please ensure the structure is correct."}

        df = df[coloane_tinta].head(5000)

        cale_folder_export = os.path.join(os.getcwd(), "PDF_Reports_Export")
        brand = date_antet.get('companie', 'PLATFORM')
        nume_client = date_antet.get('nume', 'Client')

        nume_pdf = f"Self_Exclusion_History_{brand}_-_{nume_client}"

        cale = genereaza_structura_pdf(cale_folder_export, nume_pdf, df, dimensiune_pagina, orientare_pagina,
                                       date_antet, date_subsol)
        return {"succes": True, "multiple": False, "cale": os.path.basename(cale)}
    except Exception as e:
        return {"succes": False, "eroare": str(e)}


@eel.expose
def proceseaza_tab_dep_limit_history(cale_fisier, dimensiune_pagina, orientare_pagina, date_antet, date_subsol):
    try:
        coloane_existente_in_fisier = [
            "Type", "Period", "Amount Limit", "Updated date",
            "Reset date", "New Amount Limit", "New Limit Value Date"
        ]

        eel.actualizeazaStatus("Loading Deposit Limit History data...")()
        df = citeste_si_filtreaza(cale_fisier, coloane_existente_in_fisier)

        if df is None:
            return {
                "succes": False,
                "eroare": "Invalid format or missing columns! Please verify column headers match the source data layout exactly."
            }

        df = df[coloane_existente_in_fisier].head(5000)
        df = df.rename(columns={"Amount Limit": "Amount"})

        cale_folder_export = os.path.join(os.getcwd(), "PDF_Reports_Export")
        brand = date_antet.get('companie', 'PLATFORM')
        nume_client = date_antet.get('nume', 'Client')

        nume_pdf = f"Deposit_Limit_History_{brand}_-_{nume_client}"

        cale = genereaza_structura_pdf(cale_folder_export, nume_pdf, df, dimensiune_pagina, orientare_pagina,
                                       date_antet, date_subsol)
        return {"succes": True, "multiple": False, "cale": os.path.basename(cale)}
    except Exception as e:
        return {"succes": False, "eroare": str(e)}


eel.start('index.html', size=(1100, 850))