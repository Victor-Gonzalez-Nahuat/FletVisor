import flet as ft
import pymysql
import pandas as pd
from datetime import datetime

DB_CONFIG = {
    "host": "yamanote.proxy.rlwy.net",
    "port": 51558,
    "user": "root",
    "password": "UJuewnvyQAwjjEIjUeBJPJRGyVOqKbDE",
    "database": "railway"
}

cols = [
    "Recibo", "Fecha", "Neto", "Descuento"
]

def main(page: ft.Page):
    page.title = "ERP METEORITO - Visor Web"
    page.scroll = "always"
    page.theme_mode = ft.ThemeMode.LIGHT

    filtro_txt = ft.TextField(label="Buscar por contribuyente", width=350)
    fecha_desde_val = {"value": datetime.today()}
    fecha_hasta_val = {"value": datetime.today()}

    fecha_desde_txt = ft.TextField(label="Desde", width=150, read_only=True)
    fecha_hasta_txt = ft.TextField(label="Hasta", width=150, read_only=True)

    dp_desde = ft.DatePicker(

        on_change=lambda e: actualizar_fecha(e, fecha_desde_val)
    )
    
    dp_hasta = ft.DatePicker(
        on_change=lambda e: actualizar_fecha(e, fecha_hasta_val)
    )

    def actualizar_fecha(e, fecha: dict):
        fecha["value"] = e.control.value
        fecha_str = fecha["value"].strftime('%d/%m/%Y') 

        if fecha is fecha_desde_val:
            fecha_desde_txt.value = fecha_str
        elif fecha is fecha_hasta_val:
            fecha_hasta_txt.value = fecha_str

        page.update()


    desde_fecha = ft.ElevatedButton("Desde Fecha", icon=ft.Icons.CALENDAR_MONTH, on_click=lambda _: page.open(dp_desde))
    hasta_fecha = ft.ElevatedButton("Hasta Fecha", icon=ft.Icons.CALENDAR_MONTH, on_click=lambda _: page.open(dp_hasta))

    tabla = ft.DataTable(columns=[ft.DataColumn(ft.Text(col)) for col in cols], rows=[])

    datos = []

    def cargar_datos_filtros(e=None):
        tabla.rows.clear()
        datos.clear()

        fecha_desde = fecha_desde_val["value"]
        fecha_hasta = fecha_hasta_val["value"]

        if not fecha_desde or not fecha_hasta:
            page.snack_bar = ft.SnackBar(ft.Text("Debes seleccionar ambas fechas"), open=True)
            page.update()
            return

        desde_str = fecha_desde.strftime('%y%m%d')
        hasta_str = fecha_hasta.strftime('%y%m%d')

        try:
            conexion = pymysql.connect(**DB_CONFIG)
            cursor = conexion.cursor()
            query = """
                SELECT id_recibo, id_fecha, id_neto, id_descuento
                FROM TEARMO01
                WHERE id_fecha BETWEEN %s AND %s
            """
            cursor.execute(query, (desde_str, hasta_str))
            resultados = cursor.fetchall()

            for row in resultados:
                datos.append(row)
                tabla.rows.append(
                    ft.DataRow(cells=[ft.DataCell(ft.Text(str(cell))) for cell in row])
                )
            page.update()
        except Exception as err:
            page.snack_bar = ft.SnackBar(ft.Text(f"Error: {err}"), open=True)
            page.update()


    def cargar_datos_hoy(e=None):

        hoy = datetime.today().strftime('%y%m%d')

        try:
            conexion = pymysql.connect(**DB_CONFIG)
            cursor = conexion.cursor()
            query = """
                SELECT id_recibo, id_fecha, id_neto, id_descuento
                FROM TEARMO01
                WHERE id_fecha = %s
            """
            cursor.execute(query, (hoy,))
            resultados = cursor.fetchall()

            tabla.rows.clear()
            datos.clear()

            for row in resultados:
                datos.append(row)
                tabla.rows.append(
                        ft.DataRow(cells=[ft.DataCell(ft.Text(str(cell))) for cell in row])
                )
            page.update()
        except Exception as err:
            page.snack_bar = ft.SnackBar(ft.Text(f"Error: {err}"), open=True)
            page.update()

    def buscar_por_contribuyente_y_fecha():
        tabla.rows.clear()
        datos.clear()

        fecha_desde = fecha_desde_val["value"]
        fecha_hasta = fecha_hasta_val["value"]
        filtro = filtro_txt.value.strip().lower()

        if not fecha_desde or not fecha_hasta or not filtro:
            page.snack_bar = ft.SnackBar(ft.Text("Debes seleccionar ambas fechas y escribir un contribuyente"), open=True)
            page.update()
            return

        desde_str = fecha_desde.strftime('%y%m%d')
        hasta_str = fecha_hasta.strftime('%y%m%d')

        try:
            conexion = pymysql.connect(**DB_CONFIG)
            cursor = conexion.cursor()
            query = """
                SELECT id_recibo, id_fecha, id_neto, id_descuento
                FROM TEARMO01
                WHERE id_fecha BETWEEN %s AND %s AND LOWER(id_contribuyente) LIKE %s
            """
            cursor.execute(query, (desde_str, hasta_str, f"%{filtro}%"))
            resultados = cursor.fetchall()

            for row in resultados:
                datos.append(row)
                tabla.rows.append(
                    ft.DataRow(cells=[ft.DataCell(ft.Text(str(cell))) for cell in row])
                )
            page.update()
        except Exception as err:
            page.snack_bar = ft.SnackBar(ft.Text(f"Error: {err}"), open=True)
            page.update()

    def buscar(e=None):
        filtro = filtro_txt.value.strip()
        tiene_fechas = fecha_desde_val["value"] is not None and fecha_hasta_val["value"] is not None

        if filtro and tiene_fechas:
            buscar_por_contribuyente_y_fecha()
        elif tiene_fechas:
            cargar_datos_filtros()
        else:
            cargar_datos_hoy()

    def exportar_excel(e):
        if not datos:
            page.snack_bar = ft.SnackBar(ft.Text("No hay datos para exportar."), open=True)
            page.update()
            return
        df = pd.DataFrame(datos, columns=cols)
        archivo = "exportado_recibos.xlsx"
        df.to_excel(archivo, index=False)
        page.snack_bar = ft.SnackBar(ft.Text(f"Exportado a {archivo}"), open=True)
        page.update()

    fecha_hoy = datetime.today().strftime('%d/%m/%Y')
    fecha_desde_txt.value = fecha_hoy
    fecha_hasta_txt.value = fecha_hoy

    page.add(
        ft.Row([
            filtro_txt,
        ], alignment=ft.MainAxisAlignment.CENTER),
        ft.Row([
            desde_fecha,
            hasta_fecha,
        ], alignment= ft.MainAxisAlignment.CENTER),
        ft.Row([
            fecha_desde_txt,
            fecha_hasta_txt
        ], alignment=ft.MainAxisAlignment.CENTER),
        ft.Row([
            ft.ElevatedButton("Buscar", on_click=buscar),
            ft.ElevatedButton("Exportar Excel", on_click=exportar_excel, bgcolor=ft.Colors.GREEN, color=ft.Colors.WHITE),
        ]),
        ft.Container(height=20),
        ft.Column([
            ft.Row([
                tabla
            ], width=350, scroll=ft.ScrollMode.AUTO)
        ], height=300, scroll=ft.ScrollMode.AUTO)
    )
    cargar_datos_hoy()

    

ft.app(target=main)
