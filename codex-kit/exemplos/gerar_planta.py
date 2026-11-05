"""Gera exemplos/planta.dxf (planta fictícia) para a demo da skill apoio-cad.
Uso: pip install ezdxf && python gerar_planta.py"""
import ezdxf
doc = ezdxf.new("R2010")
msp = doc.modelspace()
for nome in ["A-PAREDE", "A-PORTA", "A-TEXTO", "paredes_antigas", "Layer1"]:
    doc.layers.add(nome)  # propositalmente com nomes fora do padrão
msp.add_lwpolyline([(0,0),(6,0),(6,4),(0,4)], close=True, dxfattribs={"layer": "A-PAREDE"})
msp.add_lwpolyline([(6,0),(10,0),(10,4),(6,4)], close=True, dxfattribs={"layer": "paredes_antigas"})
msp.add_text("SALA", dxfattribs={"layer": "A-TEXTO", "height": .3}).set_placement((2,2))
msp.add_text("COZINHA", dxfattribs={"layer": "Layer1", "height": .3}).set_placement((7,2))
doc.saveas("planta.dxf")
