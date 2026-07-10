Parte VI: Analisis Logistico - Prediccion de Reabastecimiento

Contexto del Problema

El challenge actual predice el consumo diario de medicamentos (cantidad de salidas). Sin embargo, el problema real del hospital es determinar cuando y cuanto pedir para evitar quiebres de stock sin generar sobrestock.

Propuesta de Solucion

1\. Metricas Clave por Producto

Para cada producto (gtin), calcular:

Consumo promedio diario: Media movil de los ultimos 30 dias

Desviacion estandar del consumo: Para medir la variabilidad

Stock actual: Ultimo registro disponible en stock.csv

Lead time de proveedor: Tiempo entre pedido y recepcion (historico de movimientos.csv tipo E)

Stock de seguridad: Buffer para cubrir variabilidad de demanda y lead time

2\. Calculo del Punto de Reorden (ROP)

ROP = (Consumo\_promedio\_diario x Lead\_time) + Stock\_seguridad

Donde:

Stock de seguridad = Z x desviacion\_estandar x raiz(Lead\_time)

Z = Factor de servicio (ej: 1.65 para 95% de servicio)

3\. Calculo de la Cantidad a Pedir (EOQ)

EOQ = raiz((2 x Demanda\_anual x Costo\_pedido) / Costo\_mantenimiento)

Adaptado al contexto hospitalario:

Demanda anual = Consumo\_promedio\_diario x 365

Costo\_pedido = Costo administrativo de generar un pedido

Costo\_mantenimiento = Costo de mantener stock (espacio, capital inmovilizado)

4\. Implementacion Practica

Paso 1: Calcular metricas historicas para cada producto

Paso 2: Si stock\_actual es menor o igual a ROP, generar alerta de reabastecimiento

Paso 3: Usar el modelo predictivo actual para alimentar el calculo del ROP dinamico

5\. Ventajas de este Enfoque

Reduccion de quiebres de stock: El ROP dinamico basado en predicciones anticipa la demanda

Optimizacion de inventario: EOQ balancea costos de pedido vs mantenimiento

Adaptabilidad: Se ajusta a patrones estacionales y tendencias

Trazabilidad: Cada pedido se justifica con datos cuantitativos

6\. Limitaciones y Consideraciones

Lead time variable: Si los proveedores no son consistentes, el ROP debe incluir un buffer mayor

Productos de baja rotacion: Para medicamentos con consumo esporadico, usar modelos diferentes

Canasta vigente: Priorizar productos VIGENTE sobre otros en la planificacion

Linea terapeutica: Agrupar pedidos por linea para optimizar logistica

7\. Dashboard de Monitoreo

Propongo un dashboard con:

Semaforo de stock: Verde (stock mayor a ROP), Amarillo (stock cercano a ROP), Rojo (stock menor a ROP)

Prediccion de consumo: Grafico de consumo historico vs prediccion proximos 14 dias

Alertas de reabastecimiento: Lista de productos que necesitan pedido inmediato

KPIs: Dias de inventario cubierto, tasa de servicio, rotacion de inventario

Conclusion

La combinacion del modelo predictivo de consumo con las formulas de inventario (ROP + EOQ) permite transformar las predicciones en decisiones operativas concretas de reabastecimiento, optimizando el balance entre disponibilidad de medicamentos y eficiencia de costos.



