import os
from fpdf import FPDF
from fpdf.enums import XPos, YPos

class PDF(FPDF):
    def header(self):
        self.set_font("Helvetica", "B", 9)
        self.set_text_color(100, 100, 100)
        self.cell(0, 8, "VelOps Paris - Certification RNCP 39586 | Bloc 3 : Piloter un projet Data", align="R", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.set_draw_color(200, 200, 200)
        self.line(10, 18, 200, 18)
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(120, 120, 120)
        self.cell(0, 10, f"Page {self.page_no()}/{{nb}}", align="C")

# Initialisation du PDF
pdf = PDF()
pdf.alias_nb_pages()
pdf.set_auto_page_break(auto=True, margin=15)
pdf.add_page()

# Contenu HTML
html_content = """
<h1 align="center" style="color: #1A365D;">DOSSIER DE MANAGEMENT DE PROJET DATA</h1>
<h3 align="center" style="color: #2B6CB0;">Projet VelOps Paris - Systeme Intelligent de Regulation de la Flotte</h3>
<p align="center"><b>Certification RNCP 39586 - Bloc 3</b></p>
<hr>

<h2 style="color: #2C5282;">1. Cadrage, Dimensionnement & Documentation (C3.1.1, C3.1.2, C3.1.3)</h2>

<h3>1.1 Cadrage du Projet (C3.1.1)</h3>
<p><b>Problematique Metier :</b> Regulation inefficace de la flotte de velos a Paris (stations saturees ou vides), generant des penalites financieres et des surcouts logistiques.</p>
<p><b>Objectifs & Livrables :</b></p>
<ul>
    <li>Predire la demande a H+2 sur les 1 400 stations.</li>
    <li>Reduire de 35% les ruptures de service aux heures de pointe.</li>
    <li>Reduire de 15% les emissions de CO2 de la flotte logistique.</li>
    <li><b>Livrables :</b> Pipeline ETL, Modele ML (R2=0.99), Dashboard Streamlit, API REST et Dossier RGPD/RSE.</li>
</ul>
<p><b>Cadre Reglementaire :</b> Respect du RGPD (aucune PII collectee), conformite EU AI Act (risque modere avec supervision humaine) et standards Open Data LOM.</p>
<p><b>Contraintes & RSE :</b> Latence API < 200 ms, hebergement Green IT eco-efficace.</p>

<h3>1.2 Dimensionnement & Budget (C3.1.2)</h3>
<p><b>Ressources Humaines :</b> 1 Lead Data PM (0.8 ETP), 1 Data Engineer (1.0 ETP), 1 Data Scientist (1.0 ETP), 1 Dev UX (0.5 ETP), 1 Referent Metier (0.2 ETP).</p>
<p><b>Budget Global :</b> <b>118 500 EUR HT</b> sur 16 semaines (4 mois / 8 Sprints Scrum).</p>
<ul>
    <li>Personnel : 102 000 EUR</li>
    <li>Infrastructures Cloud & API : 4 500 EUR</li>
    <li>Materiel Terrain (Tablettes) : 5 000 EUR</li>
    <li>Audits (RGAA & RGPD) : 4 000 EUR</li>
    <li>Reserve Imprevus : 3 000 EUR</li>
</ul>

<hr>

<h2 style="color: #2C5282;">2. Planification & Pilotage Agile (C3.2.1, C3.2.2)</h2>

<h3>2.1 Methodologie Agile & Inclusion Handicap</h3>
<p>Projet conduit sous methode <b>Scrum</b> (Sprints de 2 semaines) avec matrice <b>RASCI</b>.</p>
<p><b>Amenagement Handicap (RQTH) :</b> Ecran haut contraste 32 pouces et lecteur NVDA pour le developpeur atteint de deficience visuelle. Support ecrit systematique lors des Daily meetings.</p>

<h3>2.2 Outils de Suivi & Indicateurs (KPIs)</h3>
<p>Suivi via Jira / Kanban : <i>Sprint Burndown Chart</i> (delais), <i>CPI</i> (couts), <i>R2 / RMSE</i> (qualite ML) et <i>Latence API</i> (< 200 ms).</p>

<hr>

<h2 style="color: #2C5282;">3. Management, Competences & Arbitrages (C3.3.1, C3.3.2, C3.3.3)</h2>

<h3>3.1 Plan de Developpement des Competences</h3>
<p>Formations FastAPI et Accessibilite RGAA realisees, avec amenagement de temps (+30% de temps pratique) pour les collaborateurs concernes.</p>

<h3>3.2 Cas d'Arbitrage (Analyse des Ecarts)</h3>
<p><b>Problematique :</b> Modele Deep Learning (LSTM) trop lent (850 ms) et surcout Cloud +40%.</p>
<p><b>Arbitrage :</b> Bascule vers <b>Random Forest + Cache Redis</b>. Resultat : Latence reduite a 85 ms, precision conservee (R2 = 0.99) et budget meintenu a 100%.</p>

<hr>

<h2 style="color: #2C5282;">4. Veille Technologique & Engagements RSE / RGPD (C3.4.1, C3.4.2)</h2>

<h3>4.1 Dispositif de Veille</h3>
<p>Flux automatise (ArXiv, CNIL, EU AI Act) pour anticiper les evolutions ethiques et legales.</p>

<h3>4.2 Plan d'Action RSE & Securite</h3>
<ul>
    <li><b>Sobriete Numerique :</b> Reentrainement conditionnel du modele (-60% de conso CPU/GPU).</li>
    <li><b>Equite Spatiale :</b> Garantie de regulation equitable sur les stations peripheriques.</li>
    <li><b>Securite :</b> Chiffrement AES-256 et cles API securisees.</li>
</ul>
"""

pdf.write_html(html_content)

# Calcul dynamique du chemin exact : Projet_VelOps/bloc_3/docs/
script_dir = os.path.dirname(os.path.abspath(__file__))
bloc3_dir = os.path.dirname(script_dir)
docs_dir = os.path.join(bloc3_dir, "docs")

os.makedirs(docs_dir, exist_ok=True)
pdf_path = os.path.join(docs_dir, "Dossier_Projet_Bloc3.pdf")

pdf.output(pdf_path)
print(f"✅ Dossier PDF généré avec succès dans : {pdf_path}")