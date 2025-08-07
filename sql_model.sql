-- 1. Table pour stocker les conversations
CREATE TABLE conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE, -- Lien vers la table des utilisateurs de Supabase Auth
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    -- Optionnel : ajouter un titre pour l'afficher dans une sidebar
    title TEXT
);

-- Rendre la table accessible via l'API Supabase
ALTER TABLE conversations ENABLE ROW LEVEL SECURITY;
-- Définir les politiques d'accès (exemple : l'utilisateur ne peut voir que ses propres conversations)
CREATE POLICY "User can view their own conversations" ON conversations
    FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "User can create conversations" ON conversations
    FOR INSERT WITH CHECK (auth.uid() = user_id);


-- 2. Créer un type ENUM pour le rôle du message, pour plus de propreté
CREATE TYPE message_role AS ENUM ('user', 'assistant');

-- 3. Table pour stocker les messages
CREATE TABLE messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID NOT NULL REFERENCES conversations(id) ON DELETE CASCADE, -- Lien vers la conversation
    role message_role NOT NULL,
    content TEXT NOT NULL,
    is_loading boolean default false, -- Indique si le message est en cours de chargement
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Rendre la table accessible via l'API Supabase
ALTER TABLE messages ENABLE ROW LEVEL SECURITY;
-- Définir les politiques d'accès
CREATE POLICY "User can view messages in their own conversations" ON messages
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM conversations
            WHERE conversations.id = messages.conversation_id
              AND conversations.user_id = auth.uid()
        )
    );
CREATE POLICY "User can create messages in their own conversations" ON messages
    FOR INSERT WITH CHECK (
        EXISTS (
            SELECT 1 FROM conversations
            WHERE conversations.id = messages.conversation_id
              AND conversations.user_id = auth.uid()
        )
    );


-- 4. Table pour stocker les étapes (steps)
-- On utilise une colonne JSONB pour stocker les détails variables (sources, query, etc.)
CREATE TABLE steps (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    message_id UUID NOT NULL REFERENCES messages(id) ON DELETE CASCADE, -- Lien vers le message
    description TEXT NOT NULL,
    agent_id TEXT, -- Ou UUID si vos agents sont dans une table
    is_loading boolean default true, -- Indique si le step est en cours de chargement
    -- Colonne magique pour stocker les données spécifiques à chaque type de step
    details JSONB,
    
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Rendre la table accessible via l'API Supabase
ALTER TABLE steps ENABLE ROW LEVEL SECURITY;
-- Définir les politiques d'accès
CREATE POLICY "User can view steps for their own messages" ON steps
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM messages
            JOIN conversations ON messages.conversation_id = conversations.id
            WHERE messages.id = steps.message_id
              AND conversations.user_id = auth.uid()
        )
    );
-- En général, les steps sont créés par le backend, donc pas besoin de politique d'INSERT pour l'utilisateur.