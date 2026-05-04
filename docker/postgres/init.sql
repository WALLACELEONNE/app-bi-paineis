CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

INSERT INTO tenants (id, nome, slug) VALUES
    (1, 'Agro BI Default', 'default')
ON CONFLICT (slug) DO NOTHING;

INSERT INTO departamentos (id, tenant_id, nome, slug) VALUES
    (1, 1, 'Contabilidade', 'contabil'),
    (2, 1, 'Financeiro',    'financeiro'),
    (3, 1, 'Vendas',        'vendas'),
    (4, 1, 'Compras',       'compras'),
    (5, 1, 'Produção',      'producao'),
    (6, 1, 'Logística',     'logistica')
ON CONFLICT DO NOTHING;
