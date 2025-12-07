#!/usr/bin/env python3
"""
Script pour exécuter la migration des champs calculés pour les crédits.
"""

from app import create_app, db

def run_migration():
    app = create_app()
    with app.app_context():
        # Execute migration SQL
        with open('migrations/add_credit_calculated_fields.sql', 'r') as f:
            migration_sql = f.read()
        
        # Split by semicolon and execute each statement
        statements = [stmt.strip() for stmt in migration_sql.split(';') if stmt.strip() and not stmt.strip().startswith('--')]
        
        for stmt in statements:
            if stmt.strip() and stmt.strip() != 'COMMIT':
                print(f'Executing: {stmt[:50]}...')
                try:
                    db.session.execute(db.text(stmt))
                    db.session.commit()
                    print('✓ Success')
                except Exception as e:
                    print(f'✗ Error: {e}')
                    db.session.rollback()
        
        print('Migration completed')

if __name__ == '__main__':
    run_migration()