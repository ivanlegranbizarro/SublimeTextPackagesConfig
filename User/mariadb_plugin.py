# archivo: Packages/User/MariaDBPlugin/mariadb_plugin.py
import sublime
import sublime_plugin
import subprocess
import json
import os
from pathlib import Path

class MariadbConnectionCommand(sublime_plugin.WindowCommand):
    def run(self):
        self.window.show_input_panel("Base de datos:", "", self.on_database_done, None, None)
    
    def on_database_done(self, database):
        self.database = database
        self.window.show_input_panel("Usuario:", "", self.on_user_done, None, None)
    
    def on_user_done(self, user):
        self.user = user
        self.window.show_input_panel("Contraseña:", "", self.on_password_done, None, None)
    
    def on_password_done(self, password):
        # Guardar credenciales temporalmente
        credentials = {
            "database": self.database,
            "user": self.user,
            "password": password
        }
        
        # Guardar en el directorio home del usuario
        creds_file = Path.home() / '.mariadb_sublime_credentials.json'
        with open(creds_file, 'w') as f:
            json.dump(credentials, f)
        
        sublime.status_message("Credenciales guardadas")

class ExecuteSqlQueryCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        # Obtener la selección actual
        selection = self.view.sel()
        if len(selection) > 0:
            query = self.view.substr(selection[0])
            if query.strip():
                try:
                    # Crear archivo temporal para la consulta
                    query_file = Path.home() / '.mariadb_sublime_query.sql'
                    with open(query_file, 'w') as f:
                        f.write(query)
                    
                    # Ejecutar script externo
                    script_content = self.get_runner_script()
                    runner_path = Path.home() / '.mariadb_sublime_runner.py'
                    with open(runner_path, 'w') as f:
                        f.write(script_content)
                    
                    # Hacer el script ejecutable
                    runner_path.chmod(0o755)
                    
                    # Ejecutar con Python del sistema
                    result = subprocess.run(
                        ['python3', str(runner_path)],
                        capture_output=True,
                        text=True
                    )
                    
                    # Mostrar resultados
                    output_view = self.view.window().create_output_panel('sql_results')
                    if result.returncode == 0:
                        output_view.run_command('append', {'characters': result.stdout})
                    else:
                        output_view.run_command('append', {'characters': f"Error: {result.stderr}"})
                    
                    self.view.window().run_command('show_panel', {'panel': 'output.sql_results'})
                    
                    # Limpiar archivos temporales
                    query_file.unlink(missing_ok=True)
                    runner_path.unlink(missing_ok=True)
                    
                except Exception as e:
                    sublime.error_message(f"Error al ejecutar la consulta: {e}")
        else:
            sublime.error_message("No hay texto seleccionado para ejecutar")

    def get_runner_script(self):
        return '''#!/usr/bin/env python3
import mariadb
import json
import sys
from pathlib import Path

def main():
    # Leer credenciales
    creds_file = Path.home() / '.mariadb_sublime_credentials.json'
    query_file = Path.home() / '.mariadb_sublime_query.sql'
    
    if not creds_file.exists():
        print("Error: Primero debes configurar las credenciales usando el comando 'MariaDB: Conectar'")
        sys.exit(1)

    with open(creds_file) as f:
        credentials = json.load(f)
    
    with open(query_file) as f:
        query = f.read()

    try:
        # Conectar a MariaDB
        conn = mariadb.connect(
            host="127.0.0.1",
            port=3306,
            user=credentials['user'],
            password=credentials['password'],
            database=credentials['database']
        )

        cursor = conn.cursor()
        cursor.execute(query)

        # Procesar resultados
        if cursor.description:  # Si hay resultados
            columns = [desc[0] for desc in cursor.description]
            results = cursor.fetchall()

            # Formatear salida
            header = " | ".join(str(col) for col in columns)
            separator = "-" * len(header)
            print(header)
            print(separator)
            
            for row in results:
                print(" | ".join(str(value) for value in row))
        else:
            print(f"Consulta ejecutada. Filas afectadas: {cursor.rowcount}")

        conn.commit()
        cursor.close()
        conn.close()

    except mariadb.Error as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
'''