'''Interface interactive (ipywidgets) de l’outil de recommandation.

Usage dans un notebook :
    from reco_tool.ui import launch
    launch()
'''

from html import escape

from .recommender import get_rules, recommander

CSS = '''<style>
.reco {border-collapse: collapse; margin-top: 10px; min-width: 760px}
.reco th {text-align: left; background: #2c3e50; color: white; padding: 6px 14px}
.reco td {padding: 6px 14px; border-bottom: 1px solid #e5e5e5}
.reco td.k {font-weight: bold; background: #f5f5f5}
.bad {color: #c62828; font-weight: bold}
.good {color: #2e7d32; font-weight: bold}
.muted {color: #777}
</style>'''

ROWS = [
    ('Layout_dominant', 'Layout recommandé'),
    ('KPI_emplacement', 'Emplacement des KPI'),
    ('Series_temporelles_emplacement', 'Emplacement de la série'),
    ('Tables_detail_emplacement', 'Emplacement de la table'),
    ('Filtres_emplacement', 'Emplacement des filtres'),
    ('Interactions_types', 'Types d’interaction'),
    ('Types_visuels', 'Type de visuel dominant'),
    ('Visuels_recommandes', 'Visuels recommandés'),
    ('Affordances_actions', 'Niveau d’affordance'),
    ('Risques_surcharge', 'Risque de surcharge'),
]

SOURCES = {
    'frequentiel': 'Fréquentiel',
    'apriori': 'Apriori',
    'grille': 'Grille',
    'elements': 'Éléments présents',
    'fallback': 'Fallback logique',
}


def confidence_text(info):
    if info['confiance'] is not None:
        return f"{info['confiance']:.1f} %".replace('.', ',')
    return info.get('note', '—')


def source_text(info):
    label = SOURCES.get(info['source'], info['source'])
    if info['source'] == 'frequentiel':
        label += f" (n={info['n']})"
    return label


def build_html(reco):
    '''Construit le tableau HTML des recommandations.'''
    lines = []
    for key, label in ROWS:
        info = reco.get(key)
        if info is None:
            lines.append(
                f'<tr><td class=k>{label}</td>'
                '<td class=muted colspan=3>Aucune règle applicable</td></tr>'
            )
            continue
        value = escape(str(info['valeur']).replace('_', ' '))
        if key == 'Risques_surcharge':
            css = 'bad' if info['valeur'] == 'Oui' else 'good'
            value = f'<span class={css}>{value}</span>'
        lines.append(
            f'<tr><td class=k>{label}</td><td>{value}</td>'
            f'<td>{confidence_text(info)}</td><td>{source_text(info)}</td></tr>'
        )
    header = '<tr><th>Recommandation</th><th>Valeur</th><th>Confiance</th><th>Source</th></tr>'
    return CSS + '<table class=reco>' + header + ''.join(lines) + '</table>'


def launch():
    '''Affiche l’interface (deux panneaux, bouton, tableau de résultats).'''
    import ipywidgets as widgets
    from IPython.display import HTML, clear_output, display

    stats = get_rules()['stats']
    print(
        f"{stats['pages']} pages · {stats['itemsets_frequents']} itemsets fréquents "
        f"· {stats['regles_apriori']} règles Apriori"
    )

    style = {'description_width': '130px'}

    def yes_no(value):
        return widgets.ToggleButtons(options=['Oui', 'Non'], value=value, style={'button_width': '150px'})

    def level_radio(value):
        return widgets.RadioButtons(
            options=['Faible', 'Moderee', 'Forte'], value=value, layout=widgets.Layout(width='auto')
        )

    def count_slider(value, description):
        return widgets.IntSlider(
            value=value, min=0, max=15, description=description, continuous_update=False,
            style=style, layout=widgets.Layout(width='330px'),
        )

    kpi_toggle = yes_no('Oui')
    nb_kpi = count_slider(4, 'Nombre de KPI :')
    serie_toggle = yes_no('Non')
    table_toggle = yes_no('Oui')
    alerte_toggle = yes_no('Non')
    nb_filtres = count_slider(4, 'Nb filtres :')
    densite = level_radio('Forte')
    couleur = level_radio('Faible')
    taille = level_radio('Faible')

    def on_kpi_change(change):
        nb_kpi.disabled = change['new'] == 'Non'

    kpi_toggle.observe(on_kpi_change, names='value')

    panel = widgets.Layout(border='1px solid #dddddd', padding='10px 20px', width='48%')
    left = widgets.VBox([
        widgets.HTML('<h3>📊 Éléments du dashboard</h3>'),
        widgets.Label('KPI présents :'), kpi_toggle, nb_kpi,
        widgets.Label('Série temporelle :'), serie_toggle,
        widgets.Label('Table détail :'), table_toggle,
        widgets.Label('Alertes :'), alerte_toggle,
        nb_filtres,
    ], layout=panel)
    right = widgets.VBox([
        widgets.HTML('<h3>🎨 Contexte visuel</h3>'),
        widgets.Label('Densité info :'), densite,
        widgets.Label('Hiérarchie couleur :'), couleur,
        widgets.Label('Hiérarchie taille :'), taille,
    ], layout=panel)

    title = widgets.HTML('<h1 style=color:#2c3e50>🎛️ Outil de recommandation Dashboard</h1>')
    run_button = widgets.Button(
        description='🔍 Obtenir recommandations', button_style='info',
        layout=widgets.Layout(width='350px', height='50px'),
    )
    results = widgets.Output()

    def on_click(_):
        with results:
            clear_output(wait=True)
            try:
                reco = recommander(
                    kpi_present=kpi_toggle.value,
                    nb_kpi=nb_kpi.value if kpi_toggle.value == 'Oui' else 0,
                    serie_present=serie_toggle.value,
                    table_present=table_toggle.value,
                    alerte_present=alerte_toggle.value,
                    nb_filtres=nb_filtres.value,
                    densite=densite.value,
                    hierarchie_couleur=couleur.value,
                    hierarchie_taille=taille.value,
                )
            except ValueError as error:
                display(HTML(f'<p class=bad>Entrée invalide : {escape(str(error))}</p>' + CSS))
                return
            display(HTML('<h3>Recommandation</h3>' + build_html(reco)))

    run_button.on_click(on_click)
    display(title, widgets.HBox([left, right]), run_button, results)
