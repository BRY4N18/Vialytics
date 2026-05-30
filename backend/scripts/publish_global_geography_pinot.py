import os
import sys
import django
import time
import zlib

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from accidentes.repositories import KafkaRepository

def get_hash_id(name: str) -> int:
    return zlib.crc32(name.encode('utf-8')) & 0x7FFFFFFF

def publish_geography():
    print("Publishing comprehensive global geography strictly to Pinot (via Kafka) - No SQLite...")
    kafka = KafkaRepository()
    ahora_ms = int(time.time() * 1000)

    # Dictionary containing all global geographical data mapped to their 2-letter ISO codes
    geography = {
        "CL": { # Chile
            "Región Metropolitana": {
                "Santiago": {
                    "Santiago": ["Avenida Providencia", "Alameda Bernardo O'Higgins", "Avenida Apoquindo"]
                }
            },
            "Valparaíso": {
                "Valparaíso": {
                    "Viña del Mar": ["Avenida San Martín", "Calle Valparaíso"]
                }
            }
        },
        "BO": { # Bolivia
            "La Paz": {
                "La Paz": {
                    "La Paz": ["Avenida 16 de Julio", "El Prado", "Calle Sagárnaga"]
                }
            },
            "Santa Cruz": {
                "Santa Cruz de la Sierra": {
                    "Santa Cruz de la Sierra": ["Avenida Cristo Redentor", "Calle Libertad"]
                }
            }
        },
        "UY": { # Uruguay
            "Montevideo": {
                "Montevideo": {
                    "Montevideo": ["Avenida 18 de Julio", "Rambla de Montevideo", "Bulevar Artigas"]
                }
            }
        },
        "PY": { # Paraguay
            "Capital": {
                "Asunción": {
                    "Asunción": ["Avenida Mariscal López", "Calle Palma", "Avenida España"]
                }
            }
        },
        "VE": { # Venezuela
            "Distrito Capital": {
                "Caracas": {
                    "Caracas": ["Avenida Bolívar", "Sabana Grande", "Avenida Francisco de Miranda"]
                }
            },
            "Zulia": {
                "Maracaibo": {
                    "Maracaibo": ["Calle 72", "Avenida 5 de Julio"]
                }
            }
        },
        "DE": { # Alemania
            "Berlín": {
                "Berlín": {
                    "Berlín": ["Kurfürstendamm", "Unter den Linden", "Friedrichstraße"]
                }
            },
            "Baviera": {
                "Múnich": {
                    "Múnich": ["Maximilianstraße", "Leopoldstraße"]
                }
            }
        },
        "FR": { # Francia
            "Isla de Francia": {
                "París": {
                    "París": ["Avenue des Champs-Élysées", "Rue de Rivoli", "Boulevard Haussmann"]
                }
            },
            "Provenza-Alpes-Costa Azul": {
                "Marsella": {
                    "Marsella": ["La Canebière", "Rue de la République"]
                }
            }
        },
        "GB": { # Reino Unido
            "Gran Londres": {
                "Londres": {
                    "Londres": ["Oxford Street", "Regent Street", "Whitehall"]
                }
            },
            "Escocia": {
                "Edimburgo": {
                    "Edimburgo": ["Royal Mile", "Princes Street"]
                }
            }
        },
        "IT": { # Italia
            "Lacio": {
                "Roma": {
                    "Roma": ["Via del Corso", "Via Condotti", "Via Nazionale"]
                }
            },
            "Lombardía": {
                "Milán": {
                    "Milán": ["Corso Como", "Via Montenapoleone", "Via della Spiga"]
                }
            }
        },
        "JP": { # Japón
            "Tokio": {
                "Tokio": {
                    "Tokio": ["Shibuya Crossing", "Ginza Dori", "Omotesando"]
                }
            },
            "Kioto": {
                "Kioto": {
                    "Kioto": ["Calle Shijo", "Calle Kawaramachi"]
                }
            }
        },
        "CN": { # China
            "Pekín": {
                "Pekín": {
                    "Pekín": ["Avenida Chang’an", "Wangfujing", "Calle Qianmen"]
                }
            },
            "Shanghái": {
                "Shanghái": {
                    "Shanghái": ["Nanjing Road", "The Bund", "Huaihai Road"]
                }
            }
        },
        "IN": { # India
            "Delhi": {
                "Nueva Delhi": {
                    "Nueva Delhi": ["Rajpath", "Connaught Place"]
                }
            },
            "Maharashtra": {
                "Mumbai": {
                    "Mumbai": ["Marine Drive", "Colaba Causeway", "Linking Road"]
                }
            }
        },
        "AU": { # Australia
            "Nueva Gales del Sur": {
                "Sídney": {
                    "Sídney": ["George Street", "Pitt Street", "Oxford Street"]
                }
            },
            "Victoria": {
                "Melbourne": {
                    "Melbourne": ["Bourke Street", "Collins Street", "Flinders Lane"]
                }
            }
        },
        "ZA": { # Sudáfrica
            "Gauteng": {
                "Johannesburgo": {
                    "Johannesburgo": ["Vilakazi Street", "Commissioner Street"]
                }
            },
            "Cabo Occidental": {
                "Ciudad del Cabo": {
                    "Ciudad del Cabo": ["Long Street", "Bree Street", "Strand Street"]
                }
            }
        },
        "EC": { # Ecuador (Republishing with EC code)
            "Pichincha": {
                "Quito": {
                    "Quito": ["Av. Amazonas", "Av. de la Prensa", "Av. 10 de Agosto", "Av. Eloy Alfaro", "Av. Patria", "Av. Simón Bolívar", "Av. Occidental"],
                    "Sangolqui": ["Av. General Rumiñahui", "Av. Ilaló", "Av. Abdón Calderón"]
                }
            },
            "Guayas": {
                "Guayaquil": {
                    "Guayaquil": ["Av. 9 de Octubre", "Av. Francisco de Orellana", "Av. de las Américas", "Av. Carlos Julio Arosemena", "Malecón 2000"],
                    "Samborondon": ["Av. Samborondón", "Av. Principal", "Calle C"]
                }
            },
            "Azuay": {
                "Cuenca": {
                    "Cuenca": ["Av. de las Américas", "Av. Remigio Crespo", "Calle Larga", "Av. Solano"]
                }
            }
        },
        "CO": { # Colombia (Republishing with CO code)
            "Cundinamarca": {
                "Bogota D.C.": {
                    "Bogota": ["Carrera 7", "Avenida de las Américas", "Calle 100", "Avenida Boyacá", "Calle 26"]
                }
            },
            "Antioquia": {
                "Medellin": {
                    "Medellin": ["Avenida El Poblado", "Avenida Las Vegas", "Calle San Juan", "Avenida Oriental"]
                }
            }
        },
        "PE": { # Perú (Republishing with PE code)
            "Lima": {
                "Lima Metropolitana": {
                    "Lima": ["Avenida Arequipa", "Avenida Javier Prado", "Avenida Abancay", "Avenida Tacna"]
                }
            },
            "Cusco": {
                "Cusco Prov": {
                    "Cusco": ["Av. El Sol", "Av. de la Cultura", "Calle de las Tiendas"]
                }
            }
        },
        "ES": { # España (Republishing with ES code)
            "Madrid": {
                "Madrid Prov": {
                    "Madrid": ["Gran Vía", "Paseo de la Castellana", "Calle de Alcalá", "Paseo del Prado"]
                }
            },
            "Catalunya": {
                "Barcelona Prov": {
                    "Barcelona": ["La Rambla", "Avinguda Diagonal", "Passeig de Gràcia", "Gran Via"]
                }
            }
        },
        "MX": { # México (Republishing with MX code)
            "Ciudad de Mexico": {
                "CDMX": {
                    "Ciudad de Mexico": ["Paseo de la Reforma", "Avenida de los Insurgentes", "Eje Central", "Avenida Juárez"]
                }
            },
            "Jalisco": {
                "Guadalajara Mnp": {
                    "Guadalajara": ["Avenida Chapultepec", "Avenida Vallarta", "Avenida López Mateos"]
                }
            }
        },
        "CA": { # Canadá (Republishing with CA code)
            "Ontario": {
                "Toronto Div": {
                    "Toronto": ["Yonge Street", "Queen Street", "Bloor Street", "Dundas Street"]
                }
            }
        },
        "AR": { # Argentina (Republishing with AR code)
            "Buenos Aires": {
                "CABA": {
                    "Buenos Aires": ["Avenida 9 de Julio", "Avenida Corrientes", "Avenida de Mayo", "Calle Florida"]
                }
            }
        },
        "BR": { # Brasil (Republishing with BR code)
            "Sao Paulo": {
                "Sao Paulo Div": {
                    "Sao Paulo": ["Avenida Paulista", "Rua Augusta", "Avenida Brigadeiro Faria Lima"]
                }
            },
            "Rio de Janeiro": {
                "Rio Div": {
                    "Rio de Janeiro": ["Avenida Atlântica", "Avenida Vieira Souto", "Rua Copacabana"]
                }
            }
        }
    }

    # Iterate & Populate Pinot via Kafka only
    for pais_code, estados in geography.items():
        # 1. Country Ingestion
        id_pais = get_hash_id(pais_code)
        payload_pais = {
            "idpais": id_pais,
            "pais": pais_code,
            "activo": True,
            "fecha_actualizacion": ahora_ms
        }
        kafka.enviar_mensaje("paises_topic", id_pais, payload_pais)
        print(f"Ingested country code: {pais_code} (Pinot ID: {id_pais})")

        for estado_name, condados in estados.items():
            # 2. State Ingestion
            id_estado = get_hash_id(f"{pais_code}_{estado_name}")
            payload_estado = {
                "idestado": id_estado,
                "estado": estado_name,
                "pais": pais_code, # Must map to 2-letter country code
                "activo": True,
                "fecha_actualizacion": ahora_ms
            }
            kafka.enviar_mensaje("estados_topic", id_estado, payload_estado)

            for condado_name, ciudades in condados.items():
                # 3. County Ingestion
                id_condado = get_hash_id(f"{estado_name}_{condado_name}")
                payload_condado = {
                    "idcondado": id_condado,
                    "condado": condado_name,
                    "estado": estado_name, # Map to State name
                    "activo": True,
                    "fecha_actualizacion": ahora_ms
                }
                kafka.enviar_mensaje("condados_topic", id_condado, payload_condado)

                for ciudad_name, calles in ciudades.items():
                    # 4. City Ingestion
                    id_ciudad = get_hash_id(f"{condado_name}_{ciudad_name}")
                    payload_ciudad = {
                        "idciudad": id_ciudad,
                        "ciudad": ciudad_name,
                        "condado": condado_name,
                        "activo": True,
                        "fecha_actualizacion": ahora_ms
                    }
                    kafka.enviar_mensaje("ciudades_topic", id_ciudad, payload_ciudad)

                    for calle_name in calles:
                        # 5. Street Ingestion
                        id_calle = get_hash_id(f"{ciudad_name}_{calle_name}")
                        payload_calle = {
                            "idcalle": id_calle,
                            "calle": calle_name,
                            "ciudad": ciudad_name,
                            "activo": True,
                            "fecha_actualizacion": ahora_ms
                        }
                        kafka.enviar_mensaje("calles_topic", id_calle, payload_calle)

    print("\nGlobal Geography successfully populated to Apache Pinot via Kafka topics!")

if __name__ == "__main__":
    publish_geography()
