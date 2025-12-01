"""
Script de prueba de rendimiento para el sistema de almacenamiento de archivos
Genera datos de prueba con Faker y mide tiempos de subida a Supabase Storage
"""
import os
import sys
import django
import time
from io import BytesIO
from datetime import datetime, timedelta
import random

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'justifacil.settings')
django.setup()

from faker import Faker
from django.core.files.base import ContentFile
from accounts.models import Usuario
from justificaciones.models import Justificacion, Documento

fake = Faker('es_ES')  # Faker en español


def crear_archivo_pdf_fake(tamano_kb=100):
    """
    Crea un archivo PDF falso para pruebas
    
    Args:
        tamano_kb: Tamaño aproximado del archivo en KB
    
    Returns:
        ContentFile con contenido binario simulado
    """
    # Generar contenido binario aleatorio
    contenido = os.urandom(tamano_kb * 1024)
    return ContentFile(contenido, name=f"documento_{fake.uuid4()}.pdf")


def crear_usuario_fake():
    """Crea un usuario estudiante falso"""
    username = fake.user_name()
    email = fake.email()
    
    usuario = Usuario.objects.create_user(
        username=username,
        email=email,
        password='password123',
        first_name=fake.first_name(),
        last_name=fake.last_name(),
        rol=Usuario.Rol.ESTUDIANTE
    )
    return usuario


def crear_justificacion_con_documento(usuario, tamano_archivo_kb=100):
    """
    Crea una justificación con documento y mide el tiempo de subida
    
    Args:
        usuario: Usuario que crea la justificación
        tamano_archivo_kb: Tamaño del archivo a subir
    
    Returns:
        tuple: (justificacion, tiempo_subida_segundos)
    """
    # Crear justificación
    fecha_inicio = fake.date_between(start_date='-30d', end_date='today')
    fecha_fin = fecha_inicio + timedelta(days=random.randint(1, 7))
    
    motivos = [
        "Enfermedad",
        "Trámites personales",
        "Emergencia familiar",
        "Cita médica",
        "Problemas de transporte"
    ]
    
    justificacion = Justificacion.objects.create(
        estudiante=usuario,
        fecha_inicio=fecha_inicio,
        fecha_fin=fecha_fin,
        motivo=random.choice(motivos),
        descripcion=fake.text(max_nb_chars=200),
        fuente='app'
    )
    
    # Crear documento y medir tiempo de subida
    archivo = crear_archivo_pdf_fake(tamano_archivo_kb)
    
    inicio = time.time()
    documento = Documento.objects.create(
        justificacion=justificacion,
        archivo=archivo
    )
    tiempo_subida = time.time() - inicio
    
    # Validar legibilidad
    documento.validar_legibilidad()
    
    return justificacion, tiempo_subida


def ejecutar_prueba_rendimiento(num_usuarios=5, num_justificaciones_por_usuario=3, tamano_archivo_kb=100):
    """
    Ejecuta una prueba de rendimiento completa
    
    Args:
        num_usuarios: Número de usuarios a crear
        num_justificaciones_por_usuario: Justificaciones por usuario
        tamano_archivo_kb: Tamaño de cada archivo
    """
    print("=" * 80)
    print("PRUEBA DE RENDIMIENTO - SUPABASE STORAGE")
    print("=" * 80)
    print(f"\nConfiguración:")
    print(f"  - Usuarios a crear: {num_usuarios}")
    print(f"  - Justificaciones por usuario: {num_justificaciones_por_usuario}")
    print(f"  - Tamaño de archivo: {tamano_archivo_kb} KB")
    print(f"  - Total de archivos: {num_usuarios * num_justificaciones_por_usuario}")
    print(f"  - Volumen total: {(num_usuarios * num_justificaciones_por_usuario * tamano_archivo_kb) / 1024:.2f} MB")
    print("\n" + "-" * 80)
    
    tiempos_subida = []
    usuarios_creados = []
    justificaciones_creadas = []
    
    tiempo_total_inicio = time.time()
    
    try:
        # Crear usuarios y justificaciones
        for i in range(num_usuarios):
            print(f"\n[Usuario {i+1}/{num_usuarios}] Creando usuario...")
            usuario = crear_usuario_fake()
            usuarios_creados.append(usuario)
            print(f"  ✓ Usuario creado: {usuario.username}")
            
            for j in range(num_justificaciones_por_usuario):
                print(f"  [Justificación {j+1}/{num_justificaciones_por_usuario}] Subiendo archivo...", end=" ")
                justificacion, tiempo_subida = crear_justificacion_con_documento(
                    usuario, 
                    tamano_archivo_kb
                )
                justificaciones_creadas.append(justificacion)
                tiempos_subida.append(tiempo_subida)
                print(f"✓ ({tiempo_subida:.2f}s)")
        
        tiempo_total = time.time() - tiempo_total_inicio
        
        # Calcular estadísticas
        print("\n" + "=" * 80)
        print("RESULTADOS")
        print("=" * 80)
        print(f"\n📊 Estadísticas de Rendimiento:")
        print(f"  - Tiempo total: {tiempo_total:.2f} segundos")
        print(f"  - Archivos subidos: {len(tiempos_subida)}")
        print(f"  - Tiempo promedio por archivo: {sum(tiempos_subida)/len(tiempos_subida):.2f}s")
        print(f"  - Tiempo mínimo: {min(tiempos_subida):.2f}s")
        print(f"  - Tiempo máximo: {max(tiempos_subida):.2f}s")
        print(f"  - Velocidad promedio: {tamano_archivo_kb / (sum(tiempos_subida)/len(tiempos_subida)):.2f} KB/s")
        
        print(f"\n📁 Datos Creados:")
        print(f"  - Usuarios: {len(usuarios_creados)}")
        print(f"  - Justificaciones: {len(justificaciones_creadas)}")
        print(f"  - Documentos: {Documento.objects.count()}")
        
        print(f"\n✅ Prueba completada exitosamente")
        
    except Exception as e:
        print(f"\n❌ Error durante la prueba: {str(e)}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Preguntar si se deben limpiar los datos
        print("\n" + "-" * 80)
        respuesta = input("\n¿Deseas eliminar los datos de prueba? (s/n): ").lower()
        
        if respuesta == 's':
            print("\nLimpiando datos de prueba...")
            for usuario in usuarios_creados:
                usuario.delete()
            print(f"✓ Eliminados {len(usuarios_creados)} usuarios y sus justificaciones")
        else:
            print("\nDatos de prueba conservados en la base de datos")
    
    print("\n" + "=" * 80)


def menu_principal():
    """Menú interactivo para ejecutar pruebas"""
    print("\n" + "=" * 80)
    print("PRUEBA DE RENDIMIENTO - SUPABASE STORAGE")
    print("=" * 80)
    print("\nOpciones de prueba:")
    print("  1. Prueba rápida (5 usuarios, 2 justificaciones, 50 KB)")
    print("  2. Prueba media (10 usuarios, 5 justificaciones, 100 KB)")
    print("  3. Prueba intensiva (20 usuarios, 10 justificaciones, 200 KB)")
    print("  4. Prueba personalizada")
    print("  5. Salir")
    
    opcion = input("\nSelecciona una opción (1-5): ")
    
    if opcion == '1':
        ejecutar_prueba_rendimiento(5, 2, 50)
    elif opcion == '2':
        ejecutar_prueba_rendimiento(10, 5, 100)
    elif opcion == '3':
        ejecutar_prueba_rendimiento(20, 10, 200)
    elif opcion == '4':
        try:
            usuarios = int(input("Número de usuarios: "))
            justificaciones = int(input("Justificaciones por usuario: "))
            tamano = int(input("Tamaño de archivo (KB): "))
            ejecutar_prueba_rendimiento(usuarios, justificaciones, tamano)
        except ValueError:
            print("❌ Valores inválidos")
    elif opcion == '5':
        print("\n¡Hasta luego!")
        return
    else:
        print("\n❌ Opción inválida")


if __name__ == "__main__":
    menu_principal()
