-- Schema creation for runs table
CREATE TABLE IF NOT EXISTS runs (
    run_id VARCHAR(255) PRIMARY KEY,
    sandbox_name VARCHAR(255) NOT NULL,
    problem_id VARCHAR(255) NOT NULL,
    state VARCHAR(50) NOT NULL,
    execution_target VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Seed row
INSERT INTO runs (run_id, sandbox_name, problem_id, state, execution_target)
VALUES ('1', 'sbx-seeddemo1', 'demo', 'deleted', 'celesto_sandbox')
ON CONFLICT (run_id) DO NOTHING;
