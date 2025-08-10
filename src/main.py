import flet as ft
from datetime import datetime, date
import requests
import pytz

API_URL = "https://api-telchac-production-45c8.up.railway.app/"
#hola
def main(page: ft.Page):
    page.theme_mode = ft.ThemeMode.LIGHT
    page.theme = ft.Theme(color_scheme_seed=ft.Colors.RED)
    page.title = "Recibos"
    page.padding = 10

    todos_los_recibos = []
    pagina_actual = 0
    tamanio_pagina = 100


    zona_horaria = pytz.timezone("America/Merida")
    hoy = datetime.now(zona_horaria).date()
    hoy_str = hoy.isoformat()

    logo = ft.Image(
        src="https://i.ibb.co/SDz9CZXS/Imagen-de-Whats-App-2025-04-22-a-las-15-46-24-f6a2c21e.jpg",
        width=60, height=60, fit=ft.ImageFit.CONTAIN
    )

    titulo_empresa = ft.Text("TELCHAC PUERTO", size=26, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE)
    titulo = ft.Text("Consulta de Recibos", size=28, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE)

    txt_fecha_desde = ft.TextField(label="Desde", read_only=True, width=150,
                                   value=hoy.strftime("%d-%m-%Y"), bgcolor=ft.Colors.WHITE)
    txt_fecha_desde.data = hoy_str

    txt_fecha_hasta = ft.TextField(label="Hasta", read_only=True, width=150,
                                   value=hoy.strftime("%d-%m-%Y"), bgcolor=ft.Colors.WHITE)
    txt_fecha_hasta.data = hoy_str

    def actualizar_fecha(txt, nueva_fecha):
        txt.data = nueva_fecha
        txt.value = datetime.fromisoformat(nueva_fecha).strftime("%d-%m-%Y")
        page.update()

    date_picker_desde = ft.DatePicker(on_change=lambda e: actualizar_fecha(txt_fecha_desde, e.data), value=date.today())
    date_picker_hasta = ft.DatePicker(on_change=lambda e: actualizar_fecha(txt_fecha_hasta, e.data), value=date.today())
    page.overlay.extend([date_picker_desde, date_picker_hasta])

    fecha_desde_btn = ft.ElevatedButton("Fecha desde", icon=ft.icons.CALENDAR_MONTH,
                                        on_click=lambda e: page.open(date_picker_desde))
    fecha_hasta_btn = ft.ElevatedButton("Fecha hasta", icon=ft.icons.CALENDAR_MONTH,
                                        on_click=lambda e: page.open(date_picker_hasta))

    contribuyente_input = ft.TextField(
        label="Filtrar por contribuyente (opcional)",
        width=400,
        text_size=14,
        border_color=ft.Colors.GREY,
        color=ft.Colors.BLACK,
        cursor_color=ft.Colors.BLACK
    )

    buscar_btn = ft.ElevatedButton("Buscar",
        width=300, height=40, icon=ft.icons.SEARCH,
        bgcolor=ft.Colors.GREEN, color=ft.Colors.WHITE, icon_color=ft.Colors.WHITE
    )
    desplegar_btn = ft.ElevatedButton("Resumen",
        width=150, height=40, icon=ft.icons.INFO,
        bgcolor=ft.Colors.AMBER, color=ft.Colors.WHITE, icon_color=ft.Colors.WHITE
    )
    buscar_btn.on_click = lambda e: buscar_producto(contribuyente_input.value)
    desplegar_btn.on_click = lambda e: mostrar_despliegue_totales()

    desplegar_dialog = ft.AlertDialog(title=ft.Text("Despliegue de Totales"))

    encabezado = ft.Container(
        content=ft.Column([
            ft.Row([logo, titulo_empresa]),
            titulo,
            ft.Row([fecha_desde_btn, fecha_hasta_btn]),
            ft.Row([txt_fecha_desde, txt_fecha_hasta]),
            ft.Row([buscar_btn, desplegar_btn], alignment=ft.MainAxisAlignment.START),
            contribuyente_input
        ]),
        padding=20,
        bgcolor=ft.Colors.RED,
        border_radius=ft.BorderRadius(0, 0, 20, 20)
    )

    resultado_card = ft.Container(content=ft.Column([], scroll=ft.ScrollMode.AUTO, height=200), padding=10)
    totales_card = ft.Container()
    loader = ft.ProgressRing(visible=False, color=ft.Colors.ORANGE, stroke_width=4)

    def formatear_fecha_yymmdd(f):
        try:
            return datetime.datetime.strptime(f, "%y%m%d").strftime("%d-%m-%Y")
        except:
            return f
        
    def cambiar_pagina(delta):
        nonlocal pagina_actual
        pagina_actual += delta
        mostrar_pagina()
        
    def mostrar_resultados(data):
        nonlocal todos_los_recibos, pagina_actual
        todos_los_recibos = data
        pagina_actual = 0
        mostrar_pagina()

    def mostrar_pagina():
        nonlocal pagina_actual, tamanio_pagina, todos_los_recibos

        inicio = pagina_actual * tamanio_pagina
        fin = inicio + tamanio_pagina
        fragmento = todos_los_recibos[inicio:fin]

        recibos_widgets = []

        for r in fragmento:
            es_cancelado = r.get("status", r.get("id_status", "0")) == "1"
            color_texto = ft.Colors.GREY if es_cancelado else ft.Colors.BLACK
            estado = "❌ CANCELADO" if es_cancelado else ""

            tarjeta = ft.Card(
                content=ft.Container(
                    content=ft.Column([
                        ft.Text(f"Recibo: {r['recibo']} {estado}", weight=ft.FontWeight.BOLD, size=18, color=color_texto),
                        ft.Text(f"Contribuyente: {r['contribuyente']}", color=color_texto),
                        ft.Text(f"Concepto: {r['concepto']}", color=color_texto),
                        ft.Text(f"Fecha: {formatear_fecha_yymmdd(r['fecha'])}", color=color_texto),
                        ft.Text(f"Neto: ${float(r['neto']):,.2f}", weight=ft.FontWeight.BOLD, color=ft.Colors.GREEN_800 if not es_cancelado else ft.Colors.GREY),
                        ft.Text(f"Descuento: ${float(r['descuento']):,.2f}", color=color_texto)
                    ]),
                    padding=15,
                    bgcolor=ft.colors.WHITE,
                    border_radius=10,
                    shadow=ft.BoxShadow(blur_radius=8, color=ft.colors.GREY_400, offset=ft.Offset(2, 2))
                ),
                elevation=2
            )
            recibos_widgets.append(tarjeta)

        botones_navegacion = []

        if pagina_actual > 0:
            botones_navegacion.append(ft.ElevatedButton("⬅️ Anteriores 100", on_click=lambda e: cambiar_pagina(-1)))

        if fin < len(todos_los_recibos):
            botones_navegacion.append(ft.ElevatedButton("Siguientes 100 ➡️", on_click=lambda e: cambiar_pagina(1)))

        resultado_card.content = ft.Column(
            recibos_widgets + [ft.Row(botones_navegacion, alignment=ft.MainAxisAlignment.CENTER)],
            spacing=10, scroll=ft.ScrollMode.ALWAYS, height=200
        )
        page.update()
    def buscar_producto(nombre_raw):
        buscar_btn.disabled = True
        loader.visible = True
        fecha_desde_btn.disabled = True
        fecha_hasta_btn.disabled = True
        desplegar_btn.visible = False
        buscar_btn.width = 300
        page.update()

        desde_date = datetime.fromisoformat(txt_fecha_desde.data).date()
        hasta_date = datetime.fromisoformat(txt_fecha_hasta.data).date()
        
        desde = desde_date.strftime("%y%m%d")  # Formato YYMMDD
        hasta = hasta_date.strftime("%y%m%d")  # Formato YYMMDD
        
        params = {"desde": desde, "hasta": hasta}

        nombre = nombre_raw.strip()
        if nombre:
            params["contribuyente"] = nombre

        cancelados = 0
        data = []

        try:
            url = f"{API_URL}recibos/filtrar" if "contribuyente" in params else f"{API_URL}recibos"
            response = requests.get(url, params=params)
            if response.status_code == 200:
                data = response.json()
                cancelados = sum(1 for r in data if r.get("status", r.get("id_status", "0")) == "1")
                mostrar_resultados(data)
            else:
                print("Error:", response.status_code, response.json().get("detail"))
        except Exception as e:
            print("Error al buscar recibos:", str(e))

        try:
            response_totales = requests.get(f"{API_URL}recibos/totales", params=params)
            if response_totales.status_code == 200:
                d = response_totales.json()
                totales_card.content = ft.Column([
                    ft.Text(f"Total Neto: ${float(d.get('total_neto', 0)):,.2f}", size=22, weight=ft.FontWeight.BOLD),
                    ft.Text(f"Total Descuento: ${float(d.get('total_descuento', 0)):,.2f}", size=16, weight=ft.FontWeight.BOLD),
                    ft.Text(f"Recibos encontrados: {len(data)}", size=14, color=ft.Colors.BLACK),
                    ft.Text(f"Recibos cancelados: {d.get('cantidad_status_1', 0)}", size=14, color=ft.Colors.RED_700)
                ])
        except Exception as e:
            print("Error al obtener totales:", str(e))

        loader.visible = False
        buscar_btn.disabled = False
        fecha_hasta_btn.disabled = False
        fecha_desde_btn.disabled = False
        buscar_btn.width = 150
        desplegar_btn.visible = True
        page.update()

    def mostrar_despliegue_totales():
        desde_date = datetime.fromisoformat(txt_fecha_desde.data).date()
        hasta_date = datetime.fromisoformat(txt_fecha_hasta.data).date()

        desde = desde_date.strftime("%y%m%d")  # Formato YYMMDD
        hasta = hasta_date.strftime("%y%m%d")  # Formato YYMMDD

        params = {"desde": desde, "hasta": hasta}
        try:
            response = requests.get(f"{API_URL}recibos/totales/despliegue", params=params)
            if response.status_code == 200:
                data = response.json()
                if not data:
                    desplegar_dialog.content = ft.Text("No se encontraron totales en este rango de fechas.")
                    page.open(desplegar_dialog)
                    return

                items = []
                for cuenta_data in data:
                    cuenta = cuenta_data.get("cuenta", "Sin cuenta")
                    total_neto = cuenta_data.get("total_neto", 0.0)
                    total_descuento = cuenta_data.get("total_descuento", 0.0)

                    items.append(ft.Text(f"Cuenta: {cuenta}", size=18, weight=ft.FontWeight.BOLD))
                    items.append(ft.Text(f"  Total Neto: ${total_neto:,.2f}", size=16))
                    items.append(ft.Text(f"  Total Descuento: ${total_descuento:,.2f}", size=16))
                    items.append(ft.Divider())  # Línea divisoria entre cuentas

                desplegar_dialog.content = ft.Column(items, height=400, scroll=ft.ScrollMode.ALWAYS)
                page.open(desplegar_dialog)  # ← Abrir aquí, después de llenar el contenido

            else:
                desplegar_dialog.content = ft.Text(f"Error al obtener datos: {response.status_code}")
                page.open(desplegar_dialog)
        except Exception as e:
            print("Error al obtener totales:", str(e))
            desplegar_dialog.content = ft.Text("Hubo un error al intentar obtener los datos.")
            page.open(desplegar_dialog)


    page.add(
        ft.Column([
            encabezado,
            loader,
            totales_card,
            resultado_card,
        ], spacing=20)
    )

    buscar_producto("")

ft.app(target=main)