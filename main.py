import flet as ft
import httpx

API_URL = "http://127.0.0.1:8000/api"

# Palette sobre et professionnelle
BG      = "#0d0d0d"
CARD    = "#161616"
SURFACE = "#1f1f1f"
BORDER  = "#2a2a2a"
OR      = "#c9a84c"
OR2     = "#e8c96a"
BLANC   = "#f0f0f0"
GRIS    = "#7a7a7a"
VERT    = "#3a9d6e"
ORANGE  = "#d4830a"
ROUGE   = "#c0392b"
BLEU    = "#2980b9"


def main(page: ft.Page):
    page.title = "NECROPOLIS — Gestion de Cimetiere"
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = BG
    page.padding = 0
    page.window_width = 1280
    page.window_height = 820

    contenu_principal = ft.Column(expand=True, scroll=ft.ScrollMode.AUTO)
    titre_page = ft.Text("Tableau de bord", size=20, weight=ft.FontWeight.W_600, color=BLANC)
    status_msg = ft.Container(visible=False)

    def show_msg(texte, couleur=VERT):
        status_msg.content = ft.Container(
            content=ft.Row([
                ft.Icon(ft.Icons.CHECK_CIRCLE if couleur == VERT else ft.Icons.ERROR_OUTLINE,
                        color=couleur, size=16),
                ft.Text(texte, color=couleur, size=13),
            ], spacing=8),
            bgcolor=SURFACE,
            border_radius=6,
            padding=12,
        )
        status_msg.visible = True
        page.update()

    # ── SIDEBAR ─────────────────────────────────────
    nav_actif = ft.Ref[str]()

    def nav_item(icone, texte, page_nom):
        def on_click(e):
            afficher_page(page_nom)
        return ft.Container(
            content=ft.Row([
                ft.Icon(icone, color=OR, size=17),
                ft.Text(texte, color=BLANC, size=13, weight=ft.FontWeight.W_400),
            ], spacing=14),
            padding=13,
            border_radius=6,
            on_click=on_click,
            ink=True,
        )

    sidebar = ft.Container(
        content=ft.Column([
            ft.Container(
                content=ft.Column([
                    ft.Container(height=24),
                    ft.Icon(ft.Icons.CHURCH, color=OR, size=36),
                    ft.Container(height=6),
                    ft.Text("NECROPOLIS", size=16, weight=ft.FontWeight.BOLD, color=OR,
                             ),
                    ft.Text("Gestion de Cimetiere", size=10, color=GRIS),
                    ft.Container(height=20),
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=0),
            ),
            ft.Container(height=1, bgcolor=BORDER),
            ft.Container(height=8),
            nav_item(ft.Icons.DASHBOARD, "Tableau de bord", "dashboard"),
            nav_item(ft.Icons.GRID_VIEW, "Caveaux", "caveaux"),
            nav_item(ft.Icons.BOOKMARK, "Reservations", "reservations"),
            nav_item(ft.Icons.PERSON, "Defunts", "defunts"),
            nav_item(ft.Icons.DESCRIPTION, "Concessions", "concessions"),
            nav_item(ft.Icons.SWAP_VERT, "Exhumations", "exhumations"),
            nav_item(ft.Icons.CREDIT_CARD, "Paiements", "paiements"),
            nav_item(ft.Icons.MAP, "Carte", "carte"),
            nav_item(ft.Icons.BAR_CHART, "Statistiques", "statistiques"),
            nav_item(ft.Icons.DOWNLOAD, "Exports", "exports"),
            ft.Container(expand=True),
            ft.Container(height=1, bgcolor=BORDER),
            ft.Container(
                content=ft.Row([
                    ft.Icon(ft.Icons.CIRCLE, color=VERT, size=8),
                    ft.Text("Systeme en ligne", color=GRIS, size=11),
                ], spacing=8),
                padding=14,
            ),
        ], spacing=2, expand=True),
        bgcolor=CARD,
        width=210,
    )

    # ── HEADER ──────────────────────────────────────
    header = ft.Container(
        content=ft.Row([
            titre_page,
            ft.Row([
                ft.Icon(ft.Icons.ACCOUNT_CIRCLE, color=OR, size=24),
                ft.Text("Admin", color=BLANC, size=13),
            ], spacing=8),
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
        bgcolor=CARD,
        padding=20,
        border=ft.Border(bottom=ft.BorderSide(1, BORDER)),
    )

    # ── COMPOSANTS ──────────────────────────────────
    def card(contenu, padding=20):
        return ft.Container(
            content=contenu,
            bgcolor=CARD,
            border_radius=10,
            padding=padding,
            border=ft.Border(
                top=ft.BorderSide(1, BORDER),
                bottom=ft.BorderSide(1, BORDER),
                left=ft.BorderSide(1, BORDER),
                right=ft.BorderSide(1, BORDER),
            ),
        )

    def stat_card(titre, valeur, couleur, icone):
        return ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Container(
                        content=ft.Icon(icone, color=couleur, size=18),
                        bgcolor=SURFACE,
                        border_radius=6,
                        padding=8,
                    ),
                    ft.Text(titre, color=GRIS, size=11),
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ft.Container(height=12),
                ft.Text(str(valeur), size=30, weight=ft.FontWeight.BOLD, color=BLANC),
            ]),
            bgcolor=CARD,
            border_radius=10,
            padding=20,
            expand=True,
            border=ft.Border(
                top=ft.BorderSide(1, BORDER),
                bottom=ft.BorderSide(1, BORDER),
                left=ft.BorderSide(1, BORDER),
                right=ft.BorderSide(1, BORDER),
            ),
        )

    def badge(texte, couleur):
        libelles = {
            "disponible": "DISPONIBLE",
            "reserve": "RESERVE",
            "occupe": "OCCUPE",
            "non_exploitable": "NON EXPLOIT.",
            "en_attente": "EN ATTENTE",
            "validee": "VALIDEE",
            "annulee": "ANNULEE",
            "demande": "DEMANDE",
        }
        label = libelles.get(texte, texte.upper().replace("_", " "))
        return ft.Container(
            content=ft.Text(label, size=10, color=BLANC, weight=ft.FontWeight.BOLD),
            bgcolor=couleur,
            border_radius=4,
            padding=6,
        )

    def separateur(texte):
        return ft.Container(
            content=ft.Row([
                ft.Text(texte, color=GRIS, size=12, weight=ft.FontWeight.W_500),
            ]),
            padding=8,
        )

    def field(label, width=150):
        return ft.TextField(
            label=label,
            width=width,
            bgcolor=SURFACE,
            color=BLANC,
            border_color=BORDER,
            
            label_style=ft.TextStyle(color=GRIS, size=12),
            text_size=13,
            border_radius=6,
            
        )

    def btn_or(texte, icone, on_click):
        return ft.FilledButton(
            texte,
            icon=icone,
            on_click=on_click,
            style=ft.ButtonStyle(bgcolor=OR, color=BG),
        )

    # ── PAGE DASHBOARD ──────────────────────────────
    def page_dashboard():
        titre_page.value = "Tableau de bord"
        stats = ft.Row(spacing=12, expand=True)
        activite = ft.Column(spacing=6)

        try:
            d = httpx.get(f"{API_URL}/dashboard").json()
            stats.controls = [
                stat_card("Total Caveaux",  d["caveaux"]["total"],       OR,     ft.Icons.GRID_VIEW),
                stat_card("Disponibles",    d["caveaux"]["disponibles"],  VERT,   ft.Icons.CHECK_CIRCLE),
                stat_card("Reserves",       d["caveaux"]["reserves"],     ORANGE, ft.Icons.PENDING),
                stat_card("Occupes",        d["caveaux"]["occupes"],      ROUGE,  ft.Icons.BLOCK),
                stat_card("Revenus (USD)",  d["revenus_estimes"],         OR2,    ft.Icons.ATTACH_MONEY),
            ]
        except:
            stats.controls = [ft.Text("Serveur non disponible", color=ROUGE)]

        try:
            res_list = httpx.get(f"{API_URL}/reservations").json()
            if res_list:
                for res in res_list[:6]:
                    col = ORANGE if res["statut"] == "en_attente" else VERT if res["statut"] == "validee" else ROUGE
                    activite.controls.append(
                        ft.Container(
                            content=ft.Row([
                                ft.Container(width=3, bgcolor=col, border_radius=2),
                                ft.Container(width=12),
                                ft.Column([
                                    ft.Text(f"Reservation #{res['id']}", color=BLANC, size=13, weight=ft.FontWeight.W_500),
                                    ft.Text(f"Caveau ID : {res['caveau_id']}", color=GRIS, size=11),
                                ], spacing=2, expand=True),
                                badge(res["statut"], col),
                            ]),
                            bgcolor=SURFACE,
                            border_radius=8,
                            padding=14,
                        )
                    )
            else:
                activite.controls.append(ft.Text("Aucune reservation", color=GRIS, size=13))
        except:
            pass

        return ft.Column([
            stats,
            ft.Container(height=24),
            separateur("ACTIVITE RECENTE"),
            card(activite),
        ], spacing=0)

    # ── PAGE CAVEAUX ────────────────────────────────
    def page_caveaux():
        titre_page.value = "Registre des Caveaux"
        f_num    = field("Numero", 110)
        f_sec    = field("Section", 110)
        f_bloc   = field("Bloc", 110)
        f_statut = ft.Dropdown(
            label="Statut", width=170, bgcolor=SURFACE, color=BLANC,
            border_color=BORDER, 
            label_style=ft.TextStyle(color=GRIS, size=12),
            options=[
                ft.dropdown.Option("disponible",     "Disponible"),
                ft.dropdown.Option("reserve",        "Reserve"),
                ft.dropdown.Option("occupe",         "Occupe"),
                ft.dropdown.Option("non_exploitable","Non exploitable"),
            ]
        )
        liste = ft.Column(spacing=6)

        def charger():
            liste.controls.clear()
            try:
                caveaux = httpx.get(f"{API_URL}/caveaux").json()
                couleurs = {"disponible": VERT, "reserve": ORANGE, "occupe": ROUGE, "non_exploitable": GRIS}
                for c in caveaux:
                    col = couleurs.get(c["statut"], BLEU)
                    liste.controls.append(
                        ft.Container(
                            content=ft.Row([
                                ft.Container(width=3, bgcolor=col, border_radius=2),
                                ft.Container(width=14),
                                ft.Column([
                                    ft.Text(f"Caveau N° {c['numero']}", color=BLANC, weight=ft.FontWeight.W_500, size=13),
                                    ft.Text(f"Section {c['section']}  •  Bloc {c['bloc']}", color=GRIS, size=11),
                                ], spacing=2, expand=True),
                                badge(c["statut"], col),
                            ]),
                            bgcolor=SURFACE,
                            border_radius=8,
                            padding=14,
                            height=64,
                        )
                    )
                if not caveaux:
                    liste.controls.append(ft.Text("Aucun caveau enregistre", color=GRIS, size=13))
            except Exception as ex:
                liste.controls.append(ft.Text(f"Erreur : {ex}", color=ROUGE))
            page.update()

        def ajouter(e):
            if not f_num.value or not f_sec.value or not f_bloc.value:
                show_msg("Remplissez tous les champs !", ROUGE)
                return
            try:
                data = {"numero": f_num.value, "section": f_sec.value,
                        "bloc": f_bloc.value, "statut": f_statut.value or "disponible"}
                r = httpx.post(f"{API_URL}/caveaux", json=data)
                if r.status_code == 200:
                    show_msg("Caveau ajoute avec succes !")
                    f_num.value = f_sec.value = f_bloc.value = ""
                    charger()
                else:
                    show_msg(str(r.json()), ROUGE)
            except Exception as ex:
                show_msg(str(ex), ROUGE)

        charger()
        return ft.Column([
            card(ft.Column([
                ft.Text("Ajouter un caveau", color=OR, size=14, weight=ft.FontWeight.W_500),
                ft.Container(height=14),
                ft.Row([f_num, f_sec, f_bloc, f_statut], spacing=10, wrap=True),
                ft.Container(height=14),
                btn_or("Ajouter", ft.Icons.ADD, ajouter),
            ])),
            ft.Container(height=18),
            separateur("LISTE DES CAVEAUX"),
            liste,
        ], spacing=0)

    # ── PAGE RESERVATIONS ───────────────────────────
    def page_reservations():
        titre_page.value = "Reservations"
        f_cav    = field("ID Caveau", 120)
        f_nom    = field("Nom defunt", 150)
        f_prenom = field("Prenom defunt", 150)
        f_date   = field("Date deces (YYYY-MM-DD)", 200)
        liste    = ft.Column(spacing=6)

        def charger():
            liste.controls.clear()
            try:
                reservations = httpx.get(f"{API_URL}/reservations").json()
                for res in reservations:
                    col = ORANGE if res["statut"] == "en_attente" else VERT if res["statut"] == "validee" else ROUGE
                    liste.controls.append(
                        ft.Container(
                            content=ft.Row([
                                ft.Container(width=3, bgcolor=col, border_radius=2),
                                ft.Container(width=14),
                                ft.Column([
                                    ft.Text(f"Reservation #{res['id']}", color=BLANC, weight=ft.FontWeight.W_500, size=13),
                                    ft.Text(f"Caveau ID : {res['caveau_id']}", color=GRIS, size=11),
                                ], spacing=2, expand=True),
                                badge(res["statut"], col),
                                ft.Container(width=8),
                                ft.IconButton(
                                    ft.Icons.CHECK_CIRCLE, icon_color=VERT,
                                    tooltip="Valider la reservation",
                                    on_click=lambda e, rid=res["id"]: valider(rid),
                                ),
                                ft.IconButton(
                                    ft.Icons.PICTURE_AS_PDF, icon_color=OR,
                                    tooltip="Telecharger la facture PDF",
                                    on_click=lambda e, rid=res["id"]: page.launch_url(f"{API_URL}/reservations/{rid}/facture"),
                                ),
                            ]),
                            bgcolor=SURFACE,
                            border_radius=8,
                            padding=12,
                        )
                    )
                if not reservations:
                    liste.controls.append(ft.Text("Aucune reservation", color=GRIS, size=13))
            except Exception as ex:
                liste.controls.append(ft.Text(f"Erreur : {ex}", color=ROUGE))
            page.update()

        def valider(rid):
            try:
                httpx.put(f"{API_URL}/reservations/{rid}/valider")
                show_msg(f"Reservation #{rid} validee !")
                charger()
            except Exception as ex:
                show_msg(str(ex), ROUGE)

        def creer(e):
            if not f_cav.value or not f_nom.value or not f_date.value:
                show_msg("Remplissez tous les champs !", ROUGE)
                return
            try:
                data = {
                    "caveau_id": int(f_cav.value),
                    "nom_defunt": f_nom.value,
                    "prenom_defunt": f_prenom.value,
                    "date_deces": f_date.value,
                }
                r = httpx.post(f"{API_URL}/reservations", json=data)
                if r.status_code == 200:
                    show_msg("Reservation creee avec succes !")
                    f_cav.value = f_nom.value = f_prenom.value = f_date.value = ""
                    charger()
                else:
                    show_msg(str(r.json()), ROUGE)
            except Exception as ex:
                show_msg(str(ex), ROUGE)

        charger()
        return ft.Column([
            card(ft.Column([
                ft.Text("Nouvelle reservation", color=OR, size=14, weight=ft.FontWeight.W_500),
                ft.Container(height=14),
                ft.Row([f_cav, f_nom, f_prenom, f_date], spacing=10, wrap=True),
                ft.Container(height=14),
                btn_or("Creer la reservation", ft.Icons.SAVE, creer),
            ])),
            ft.Container(height=18),
            separateur("LISTE DES RESERVATIONS"),
            liste,
        ], spacing=0)

    # ── PAGE DEFUNTS ────────────────────────────────
    def page_defunts():
        titre_page.value = "Defunts"
        liste = ft.Column(spacing=6)

        try:
            defunts = httpx.get(f"{API_URL}/caveaux").json()
            # On charge depuis l'admin Django — liste via API reservations
            reservations = httpx.get(f"{API_URL}/reservations").json()
            if reservations:
                for res in reservations:
                    liste.controls.append(
                        ft.Container(
                            content=ft.Row([
                                ft.Container(width=3, bgcolor=OR, border_radius=2),
                                ft.Container(width=14),
                                ft.Column([
                                    ft.Text(f"Defunt lie a la Reservation #{res['id']}", color=BLANC, weight=ft.FontWeight.W_500, size=13),
                                    ft.Text(f"Caveau ID : {res['caveau_id']}  •  Statut reservation : {res['statut']}", color=GRIS, size=11),
                                ], spacing=2, expand=True),
                                badge(res["statut"], ORANGE if res["statut"] == "en_attente" else VERT),
                            ]),
                            bgcolor=SURFACE,
                            border_radius=8,
                            padding=14,
                        )
                    )
            else:
                liste.controls.append(ft.Text("Aucun defunt enregistre", color=GRIS, size=13))
        except Exception as ex:
            liste.controls.append(ft.Text(f"Erreur : {ex}", color=ROUGE))

        return ft.Column([
            card(ft.Column([
                ft.Text("Les defunts sont enregistres automatiquement lors d'une reservation.", color=GRIS, size=13),
                ft.Text("Pour ajouter un defunt, creez une reservation avec ses informations.", color=GRIS, size=13),
            ])),
            ft.Container(height=18),
            separateur("REGISTRE DES DEFUNTS"),
            liste,
        ], spacing=0)

    # ── PAGE PAIEMENTS ──────────────────────────────
    def page_paiements():
        titre_page.value = "Paiements"
        f_res     = field("ID Reservation", 160)
        f_tel     = field("Numero telephone", 180)
        f_montant = field("Montant (USD)", 140)
        f_methode = ft.Dropdown(
            label="Methode de paiement", width=210,
            bgcolor=SURFACE, color=BLANC,
            border_color=BORDER, 
            label_style=ft.TextStyle(color=GRIS, size=12),
            options=[
                ft.dropdown.Option("airtel_money", "Airtel Money"),
                ft.dropdown.Option("mpesa",        "M-Pesa"),
                ft.dropdown.Option("especes",      "Especes"),
                ft.dropdown.Option("virement",     "Virement bancaire"),
            ]
        )
        resultat = ft.Column()

        def payer(e):
            try:
                montant = float(f_montant.value) if f_montant.value else 150.0
                data = {
                    "reservation_id": int(f_res.value),
                    "methode": f_methode.value,
                    "montant": montant,
                    "numero_telephone": f_tel.value,
                }
                r = httpx.post(f"{API_URL}/paiement/simuler", json=data)
                res = r.json()
                resultat.controls = [
                    ft.Container(
                        content=ft.Column([
                            ft.Row([
                                ft.Icon(ft.Icons.CHECK_CIRCLE, color=VERT, size=24),
                                ft.Text("Paiement simule avec succes", color=VERT, size=15, weight=ft.FontWeight.W_600),
                            ], spacing=10),
                            ft.Container(height=12),
                            ft.Text(f"Methode   :  {res.get('message', '')}", color=BLANC, size=13),
                            ft.Text(f"Montant   :  {res.get('montant', '')} USD", color=BLANC, size=13),
                            ft.Text(f"Reference :  {res.get('transaction_id', '')}", color=OR, size=13, weight=ft.FontWeight.BOLD),
                        ]),
                        bgcolor=SURFACE,
                        border_radius=10,
                        padding=20,
                    )
                ]
                page.update()
            except Exception as ex:
                show_msg(str(ex), ROUGE)

        return ft.Column([
            card(ft.Column([
                ft.Text("Simulation de paiement", color=OR, size=14, weight=ft.FontWeight.W_500),
                ft.Text("Airtel Money  •  M-Pesa  •  Especes  •  Virement", color=GRIS, size=11),
                ft.Container(height=16),
                ft.Row([f_res, f_methode, f_tel, f_montant], spacing=10, wrap=True),
                ft.Container(height=14),
                btn_or("Simuler le paiement", ft.Icons.SEND, payer),
            ])),
            ft.Container(height=16),
            resultat,
        ], spacing=0)

    # ── PAGE CARTE ──────────────────────────────────
    def page_carte():
        titre_page.value = "Carte Interactive"

        import webbrowser

        def ouvrir_carte(e):
            webbrowser.open("http://127.0.0.1:8000/api/carte")

        return ft.Column([
            card(ft.Column([
                ft.Text("Carte geographique des caveaux", color=OR, size=14, weight=ft.FontWeight.W_500),
                ft.Container(height=6),
                ft.Text("Cliquez sur la carte pour voir les coordonnees d'un point.", color=GRIS, size=12),
                ft.Container(height=12),
                ft.Row([
                    ft.Row([ft.Container(width=12, height=12, bgcolor=VERT, border_radius=2), ft.Text("Disponible", color=BLANC, size=12)], spacing=6),
                    ft.Row([ft.Container(width=12, height=12, bgcolor=ORANGE, border_radius=2), ft.Text("Reserve", color=BLANC, size=12)], spacing=6),
                    ft.Row([ft.Container(width=12, height=12, bgcolor=ROUGE, border_radius=2), ft.Text("Occupe", color=BLANC, size=12)], spacing=6),
                    ft.Row([ft.Container(width=12, height=12, bgcolor=GRIS, border_radius=2), ft.Text("Non exploitable", color=BLANC, size=12)], spacing=6),
                ], spacing=20),
                ft.Container(height=16),
                ft.Text("http://127.0.0.1:8000/api/carte", color=GRIS, size=11),
                ft.Container(height=8),
                ft.FilledButton(
                    "Ouvrir la carte interactive",
                    icon=ft.Icons.MAP,
                    on_click=ouvrir_carte,
                    style=ft.ButtonStyle(bgcolor=OR, color=BG),
                ),
            ])),
        ], spacing=0)

    # ── PAGE STATISTIQUES ───────────────────────────
    def page_statistiques():
        titre_page.value = "Statistiques"
        contenu = ft.Column(spacing=10)

        try:
            d = httpx.get(f"{API_URL}/dashboard").json()
            cav = d["caveaux"]
            total = cav["total"] or 1

            def barre(label, valeur, total, couleur):
                pct = int((valeur / total) * 100) if total > 0 else 0
                return ft.Column([
                    ft.Row([
                        ft.Text(label, color=BLANC, size=12, width=160),
                        ft.Text(f"{valeur}  ({pct}%)", color=couleur, size=12, weight=ft.FontWeight.W_500),
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    ft.Container(height=4),
                    ft.Container(
                        content=ft.Container(width=max(4, int(pct * 4)), height=6, bgcolor=couleur, border_radius=3),
                        bgcolor=SURFACE,
                        border_radius=3,
                        height=6,
                    ),
                ], spacing=0)

            contenu.controls = [
                card(ft.Column([
                    ft.Text("Occupation des caveaux", color=OR, size=14, weight=ft.FontWeight.W_500),
                    ft.Container(height=16),
                    barre("Disponibles",     cav["disponibles"],  total, VERT),
                    ft.Container(height=12),
                    barre("Reserves",        cav["reserves"],     total, ORANGE),
                    ft.Container(height=12),
                    barre("Occupes",         cav["occupes"],      total, ROUGE),
                    ft.Container(height=12),
                    barre("Non exploitables",cav["non_exploitables"], total, GRIS),
                    ft.Container(height=16),
                    ft.Text(f"Taux d'occupation global : {cav.get('taux_occupation', 0)} %",
                             color=OR2, size=13, weight=ft.FontWeight.W_500),
                ])),
                ft.Container(height=14),
                card(ft.Column([
                    ft.Text("Finances", color=OR, size=14, weight=ft.FontWeight.W_500),
                    ft.Container(height=12),
                    ft.Row([
                        ft.Column([
                            ft.Text("Revenus estimes", color=GRIS, size=11),
                            ft.Text(f"{d['revenus_estimes']} USD", color=BLANC, size=22, weight=ft.FontWeight.BOLD),
                        ]),
                        ft.Column([
                            ft.Text("Reservations totales", color=GRIS, size=11),
                            ft.Text(str(d["reservations"]["total"]), color=BLANC, size=22, weight=ft.FontWeight.BOLD),
                        ]),
                        ft.Column([
                            ft.Text("Concessions actives", color=GRIS, size=11),
                            ft.Text(str(d["concessions"]), color=BLANC, size=22, weight=ft.FontWeight.BOLD),
                        ]),
                    ], spacing=40),
                ])),
            ]
        except Exception as ex:
            contenu.controls = [ft.Text(f"Erreur : {ex}", color=ROUGE)]

        return contenu

    # ── PAGE CONCESSIONS ────────────────────────────
    def page_concessions():
        titre_page.value = "Concessions"
        f_cav   = field("ID Caveau", 120)
        f_type  = ft.Dropdown(
            label="Type", width=190, bgcolor=SURFACE, color=BLANC,
            border_color=BORDER, 
            label_style=ft.TextStyle(color=GRIS, size=12),
            options=[
                ft.dropdown.Option("temporaire",  "Temporaire"),
                ft.dropdown.Option("perpetuelle", "Perpetuelle"),
            ]
        )
        f_debut = field("Date debut (YYYY-MM-DD)", 190)
        f_fin   = field("Date fin (YYYY-MM-DD)",   190)

        def creer(e):
            try:
                data = {
                    "caveau_id":        int(f_cav.value),
                    "type_concession":  f_type.value,
                    "date_debut":       f_debut.value,
                    "date_fin":         f_fin.value or None,
                }
                r = httpx.post(f"{API_URL}/concessions", json=data)
                if r.status_code == 200:
                    show_msg("Concession creee avec succes !")
                    f_cav.value = f_debut.value = f_fin.value = ""
                    page.update()
                else:
                    show_msg(str(r.json()), ROUGE)
            except Exception as ex:
                show_msg(str(ex), ROUGE)

        return ft.Column([
            card(ft.Column([
                ft.Text("Nouvelle concession funeraire", color=OR, size=14, weight=ft.FontWeight.W_500),
                ft.Text("Attribution, renouvellement et suivi des contrats de concession.", color=GRIS, size=12),
                ft.Container(height=16),
                ft.Row([f_cav, f_type, f_debut, f_fin], spacing=10, wrap=True),
                ft.Container(height=14),
                btn_or("Creer la concession", ft.Icons.SAVE, creer),
            ])),
        ], spacing=0)

    # ── PAGE EXHUMATIONS ────────────────────────────
    def page_exhumations():
        titre_page.value = "Exhumations"
        f_cav   = field("ID Caveau", 120)
        f_def   = field("ID Defunt",  120)
        f_motif = field("Motif de la demande", 360)

        def creer(e):
            try:
                data = {
                    "caveau_id": int(f_cav.value),
                    "defunt_id": int(f_def.value),
                    "motif":     f_motif.value,
                }
                r = httpx.post(f"{API_URL}/exhumations", json=data)
                if r.status_code == 200:
                    show_msg("Demande d'exhumation soumise !")
                    f_cav.value = f_def.value = f_motif.value = ""
                    page.update()
                else:
                    show_msg(str(r.json()), ROUGE)
            except Exception as ex:
                show_msg(str(ex), ROUGE)

        return ft.Column([
            card(ft.Column([
                ft.Text("Demande d'exhumation", color=OR, size=14, weight=ft.FontWeight.W_500),
                ft.Text("Enregistrement de la demande avec validation administrative et tracabilite complete.", color=GRIS, size=12),
                ft.Container(height=16),
                ft.Row([f_cav, f_def, f_motif], spacing=10, wrap=True),
                ft.Container(height=14),
                btn_or("Soumettre la demande", ft.Icons.SEND, creer),
            ])),
            ft.Container(height=14),
            card(ft.Column([
                ft.Text("Document legal", color=OR, size=13, weight=ft.FontWeight.W_500),
                ft.Container(height=8),
                ft.Text("Apres validation, une autorisation d'exhumation sera generee automatiquement.", color=GRIS, size=12),
            ])),
        ], spacing=0)

    # ── PAGE EXPORTS ────────────────────────────────
    def page_exports():
        titre_page.value = "Exports"

        def export_btn(label, url, couleur):
            return ft.OutlinedButton(
                label,
                on_click=lambda e: page.launch_url(url),
                style=ft.ButtonStyle(
                    color=couleur,
                    side=ft.BorderSide(1, couleur),
                ),
            )

        return ft.Column([
            card(ft.Column([
                ft.Text("Extraction des registres", color=OR, size=14, weight=ft.FontWeight.W_500),
                ft.Text("Exportez vos donnees en CSV ou Excel pour archivage et reporting.", color=GRIS, size=12),
                ft.Container(height=18),
                ft.Text("Caveaux", color=BLANC, size=12, weight=ft.FontWeight.W_500),
                ft.Container(height=8),
                ft.Row([
                    export_btn("CSV  — Caveaux",  f"{API_URL}/export/caveaux/csv",   BLEU),
                    export_btn("Excel — Caveaux", f"{API_URL}/export/caveaux/excel", VERT),
                ], spacing=10),
                ft.Container(height=16),
                ft.Text("Reservations", color=BLANC, size=12, weight=ft.FontWeight.W_500),
                ft.Container(height=8),
                ft.Row([
                    export_btn("CSV  — Reservations", f"{API_URL}/export/reservations/csv", BLEU),
                ], spacing=10),
            ])),
        ], spacing=0)

    # ── NAVIGATION ──────────────────────────────────
    def afficher_page(nom):
        contenu_principal.controls.clear()
        status_msg.visible = False
        pages = {
            "dashboard":    page_dashboard,
            "caveaux":      page_caveaux,
            "reservations": page_reservations,
            "defunts":      page_defunts,
            "paiements":    page_paiements,
            "carte":        page_carte,
            "statistiques": page_statistiques,
            "concessions":  page_concessions,
            "exhumations":  page_exhumations,
            "exports":      page_exports,
        }
        if nom in pages:
            contenu_principal.controls.append(pages[nom]())
        contenu_principal.controls.append(ft.Container(height=24))
        contenu_principal.controls.append(status_msg)
        page.update()

    # ── LAYOUT GLOBAL ───────────────────────────────
    page.add(
        ft.Row([
            sidebar,
            ft.Container(width=1, bgcolor=BORDER),
            ft.Column([
                header,
                ft.Container(
                    content=contenu_principal,
                    expand=True,
                    padding=24,
                ),
            ], expand=True, spacing=0),
        ], expand=True, spacing=0)
    )

    afficher_page("dashboard")


ft.app(target=main)
