# Surtilandia Ecommerce + Panel Administrativo Design

**Fecha:** 2026-04-22

## Objetivo

Construir una base seria para Surtilandia como ecommerce web con dos superficies conectadas a una misma base central:

- Una tienda pública donde el cliente navega productos, agrega al carrito, compra como invitado y consulta su pedido por ID.
- Un panel administrativo privado donde el equipo gestiona productos, pedidos, clientes, reportes y seguimiento operativo.

La primera entrega debe sentirse como una demo funcional de negocio, no como una maqueta estática. Debe quedar preparada para evolucionar después hacia una app más completa sin rehacer el modelo principal.

## Contexto y alcance de esta fase

El proyecto actual es una landing estática en `index.html`, `main.js` y `styles.css`. La siguiente fase deja de ser solo una vitrina visual y pasa a ser una aplicación web con persistencia central entre dispositivos.

Esta fase cubre:

- Catálogo conectado a productos reales.
- Detalle de producto con precio, stock, referencia, descripción e imágenes.
- Carrito y checkout como invitado.
- Registro de pedidos con ID público.
- Seguimiento del pedido por ID.
- Panel admin con login compartido.
- Gestión de productos.
- Gestión de pedidos con estados simples.
- Base de datos de clientes.
- Reportes de ventas.
- Preparación de pago online con Wompi.
- Opción de pago contra entrega.
- Gestión manual de envío nacional para la demo.

Esta fase no cubre todavía:

- Tarifas automáticas por transportadora y ubicación.
- Integración final de Wompi en producción.
- Múltiples roles administrativos.
- Sincronización con empresas de envío.
- App móvil nativa.
- Automatizaciones avanzadas de notificaciones.

## Enfoque aprobado

Se adopta un enfoque de ecommerce web con backend real y base de datos central. La tienda pública, el checkout, el seguimiento del pedido y el panel administrativo consumirán la misma fuente de datos.

Esta decisión se tomó porque el cliente hará pedidos desde un dispositivo distinto al del administrador. Por eso la solución ya no puede depender de almacenamiento local del navegador.

## Arquitectura funcional

La solución se divide en cuatro bloques:

### 1. Tienda pública

Superficie orientada al cliente final. Debe incluir:

- Inicio y catálogo.
- Filtros y búsqueda.
- Detalle de producto.
- Carrito.
- Checkout como invitado.
- Confirmación del pedido.
- Consulta del pedido por ID.

### 2. Backend central

Capa responsable de:

- Exponer datos del catálogo a la tienda.
- Registrar pedidos.
- Descontar stock.
- Guardar clientes.
- Permitir autenticación del panel admin.
- Entregar reportes y listados administrativos.
- Preparar el punto de integración de pagos y envíos.

### 3. Base de datos central

Debe ser relacional y preparada para mucho volumen informativo. El diseño se apoya en entidades normalizadas para productos, clientes, pedidos, líneas de pedido e historial operativo. La base debe soportar crecimiento de catálogo, histórico de ventas y consultas administrativas sin cambiar el modelo principal.

### 4. Panel administrativo

Superficie privada protegida por login con un único usuario compartido. Debe concentrar:

- Resumen de ventas y pedidos.
- Gestión completa de productos.
- Gestión de pedidos.
- Base de datos de clientes.
- Reportes.
- Registro manual de datos de envío para la demo.

## Dirección técnica de alto nivel

La implementación debe migrar el proyecto desde la web estática actual hacia una aplicación web con:

- Frontend público para la tienda.
- Frontend privado para administración.
- API central.
- Base de datos SQL central.

El modelo debe quedar desacoplado de integraciones externas específicas. Pagos, envíos e imágenes deben entrar a través de adaptadores para poder perfeccionarlos después sin rediseñar la base del negocio.

## Usuarios del sistema

### Cliente invitado

Puede:

- Navegar el catálogo.
- Ver detalle de producto.
- Agregar productos al carrito.
- Completar un checkout sin crear cuenta.
- Elegir método de pago.
- Recibir un ID de pedido.
- Consultar el estado del pedido por ID.

### Administrador

Usa un solo acceso compartido para el equipo. Puede:

- Iniciar sesión con usuario y contraseña.
- Crear, editar y desactivar productos.
- Ajustar stock.
- Revisar pedidos.
- Actualizar estados.
- Ver clientes registrados por compra.
- Consultar reportes de ventas.
- Registrar datos manuales de envío.

## Módulos funcionales

### Catálogo y detalle de producto

Cada producto debe mostrar como mínimo:

- Nombre.
- Referencia.
- Categoría.
- Precio.
- Stock.
- Descripción corta.
- Detalles.
- Imagen principal.
- Galería opcional.

La tienda debe reflejar en tiempo real lo que el administrador publique o actualice desde el panel.

### Carrito

Debe permitir:

- Agregar productos.
- Ajustar cantidades.
- Eliminar productos.
- Ver subtotales y total.
- Bloquear cantidades superiores al stock disponible.

### Checkout como invitado

El checkout no exige cuenta. Debe pedir datos normales de ecommerce:

- Nombre completo.
- Teléfono.
- Correo electrónico.
- Ciudad.
- Dirección.
- Información complementaria de entrega si aplica.

También debe pedir:

- Método de pago.
- Confirmación del resumen del pedido.

### Métodos de pago

La solución debe contemplar dos métodos:

- `Wompi`: se deja preparado como pago online integrado, pero la configuración final se perfeccionará después.
- `Contra entrega`: pago en efectivo al momento de recibir.

El pedido debe registrar tanto el método de pago elegido como su estado de pago. El flujo de estados del pedido no sustituye la información de pago.

### Seguimiento por ID

El cliente debe poder consultar el estado de su pedido usando el mismo ID público que recibe al confirmar la compra. La consulta debe mostrar, como mínimo:

- ID del pedido.
- Estado actual.
- Fecha de creación.
- Resumen de productos.
- Método de pago.

### Panel de productos

Debe permitir:

- Crear productos.
- Editar productos existentes.
- Ajustar stock.
- Cambiar precio.
- Gestionar referencia.
- Gestionar descripción y detalles.
- Gestionar imagen principal y galería como URLs persistidas en base de datos.
- Activar o desactivar visibilidad del producto.

La persistencia de imágenes se diseñará con URLs en la base para que más adelante pueda conectarse a un almacenamiento más robusto sin cambiar el esquema central.

### Panel de pedidos

Debe permitir:

- Ver listado de pedidos.
- Buscar por ID, cliente o estado.
- Ver detalle completo del pedido.
- Cambiar estado.
- Registrar notas operativas.
- Registrar transportadora y número de guía de forma manual en esta fase.

### Panel de clientes

Debe consolidar compradores creados a partir de pedidos. Cada ficha de cliente debe poder mostrar:

- Nombre.
- Teléfono.
- Correo.
- Dirección principal.
- Ciudad.
- Historial de compras asociado.

### Reportes de ventas

La primera versión debe incluir reportes operativos suficientes para demo y validación:

- Total de ventas en un período.
- Número de pedidos.
- Productos más vendidos.
- Pedidos por estado.
- Alertas básicas de stock bajo.

## Modelo de datos

### Producto

Campos mínimos:

- `id` interno.
- `reference` única.
- `name`.
- `slug`.
- `category`.
- `price`.
- `stock`.
- `shortDescription`.
- `details`.
- `primaryImageUrl`.
- `galleryImageUrls`.
- `isActive`.
- `createdAt`.
- `updatedAt`.

### Cliente

Campos mínimos:

- `id` interno.
- `fullName`.
- `phone`.
- `email`.
- `city`.
- `address`.
- `addressNotes`.
- `createdAt`.
- `updatedAt`.

### Pedido

Campos mínimos:

- `id` interno.
- `publicOrderId` visible al cliente.
- `customerId`.
- `status`.
- `paymentMethod`.
- `paymentStatus`.
- `shippingCarrier`.
- `shippingGuide`.
- `shippingCity`.
- `shippingAddressSnapshot`.
- `shippingNotes`.
- `subtotal`.
- `shippingAmount`.
- `total`.
- `createdAt`.
- `updatedAt`.

### Línea de pedido

Campos mínimos:

- `id` interno.
- `orderId`.
- `productId`.
- `productNameSnapshot`.
- `productReferenceSnapshot`.
- `unitPriceSnapshot`.
- `quantity`.
- `subtotal`.

### Historial de pedido

Campos mínimos:

- `id` interno.
- `orderId`.
- `fromStatus`.
- `toStatus`.
- `note`.
- `createdAt`.

### Configuración administrativa

Campos mínimos:

- `id` interno.
- `adminUsername`.
- `adminPasswordHash`.
- `createdAt`.
- `updatedAt`.

## Reglas clave del negocio

### Estados del pedido

La ruta funcional aprobada para esta fase es:

- `Pendiente`
- `Confirmado`
- `Enviado`
- `Entregado`

El seguimiento del cliente debe reflejar exactamente uno de estos estados.

### Estado de pago

Debe mantenerse separado del estado del pedido. Como mínimo debe contemplar:

- `pending`
- `paid`
- `failed`

Esto permite que un pedido pueda estar `Pendiente` con Wompi aún no completado, pasar a `paid` cuando Wompi confirme el pago o quedar en `pending` cuando el método elegido sea contra entrega. El hecho de ser contra entrega se expresa en `paymentMethod`, no en `paymentStatus`.

### Generación de ID de pedido

Cada pedido debe tener:

- Un identificador interno estable para la base.
- Un `publicOrderId` legible para cliente y administrador.

Ese `publicOrderId` será el mismo usado en:

- Confirmación de compra.
- Búsqueda administrativa.
- Seguimiento público.

### Inventario

El stock debe validarse antes de confirmar el pedido. Cuando el pedido queda registrado, el stock se descuenta. Si un producto ya no tiene unidades disponibles, no debe poder completarse la compra.

## Flujos operativos

### Flujo del cliente

1. Navega productos.
2. Revisa detalle.
3. Agrega al carrito.
4. Completa checkout como invitado.
5. Elige Wompi o contra entrega.
6. Confirma el pedido.
7. Recibe el `publicOrderId`.
8. Consulta el estado más tarde por ID.

### Flujo del administrador

1. Inicia sesión.
2. Recibe un nuevo pedido en el panel.
3. Revisa productos, datos del cliente y método de pago.
4. Gestiona manualmente envío y guía si aplica.
5. Actualiza el estado del pedido.
6. Consulta ventas, clientes y stock.

## Envíos nacionales en esta fase

La demo debe incluir el concepto de envío nacional y los campos para operarlo, pero no implementará aún el cálculo automático de tarifa por transportadora y ubicación.

La base y el panel sí deben dejar listos los datos para crecer hacia ese escenario:

- Transportadora.
- Ciudad de destino.
- Guía.
- Valor de envío.
- Notas de despacho.

## Autenticación y seguridad

El panel administrativo debe estar protegido con autenticación. En esta fase habrá un solo acceso compartido. La implementación debe:

- Solicitar usuario y contraseña antes de entrar al panel.
- Proteger rutas administrativas.
- Mantener sesión persistente mientras sea válida.
- Evitar acceso directo al panel sin login.

Las credenciales definitivas de demo se generarán durante la implementación y se entregarán al usuario cuando el panel quede funcional.

## Manejo de errores y validaciones

La experiencia debe cubrir como mínimo estos casos:

- No permitir checkout con campos obligatorios vacíos.
- No permitir cantidades mayores al stock.
- No permitir acceder al panel con credenciales inválidas.
- Mostrar mensaje claro si el `publicOrderId` no existe.
- No marcar como pagado un pedido Wompi si el pago no se confirma.
- Mostrar estados vacíos con mensajes útiles cuando no haya productos, pedidos o clientes.

## Criterios de aceptación de la demo

La demo se considera válida cuando cumpla esto de punta a punta:

1. El administrador puede crear y editar productos desde el panel.
2. Los productos publicados se reflejan en la tienda pública.
3. Un cliente puede comprar como invitado.
4. El sistema genera un `publicOrderId` al confirmar la compra.
5. El pedido queda visible en el panel administrativo.
6. El stock se actualiza después del pedido.
7. El administrador puede cambiar el estado del pedido.
8. El cliente puede consultar ese estado por ID.
9. El panel muestra clientes registrados por compra.
10. El panel muestra reportes básicos de ventas.

## Criterios de calidad para la futura evolución

La base debe quedar preparada para:

- Integrar Wompi completamente.
- Añadir cálculo automático de envíos.
- Crear más roles administrativos.
- Añadir notificaciones.
- Llevar la misma lógica a una app futura.

Esto implica que el esquema de datos, la API y la separación entre tienda, administración e integraciones no se deben diseñar como algo temporal o desechable.

## No objetivos de esta fase

Para evitar sobrecargar la primera implementación, quedan fuera:

- Sistema de cupones.
- Wishlist.
- Opiniones de productos.
- Multiusuario con permisos.
- Tarifador avanzado de transportadoras.
- Automatización de facturación.
- Integración con WhatsApp como canal principal de compra.

## Resumen de diseño aprobado

Surtilandia pasará de una landing estática a una aplicación web ecommerce con backend real y base central. El cliente comprará desde la tienda como invitado y recibirá un ID de pedido. El administrador entrará a un panel protegido por usuario y contraseña para gestionar productos, pedidos, clientes, reportes y envíos manuales. La base quedará lista para perfeccionar pagos, transportadoras y una futura app sin rehacer el núcleo del sistema.
