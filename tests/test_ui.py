from reco_tool.recommender import recommander
from reco_tool.ui import build_html


def test_tableau_cas_usage_1():
    reco = recommander(
        kpi_present='Oui', nb_kpi=4, serie_present='Oui', table_present='Oui',
        densite='Forte', hierarchie_couleur='Faible', hierarchie_taille='Faible',
    )
    html = build_html(reco)
    assert 'Risque de surcharge' in html
    assert '<span class=bad>Oui</span>' in html
    assert '100,0 %' in html
    assert 'Fallback logique' in html


def test_regle_absente_affiche_un_message():
    html = build_html({})
    assert html.count('Aucune règle applicable') == 10
