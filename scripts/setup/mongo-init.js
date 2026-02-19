// MongoDB initialization script
// This script runs when the container is first started

// Switch to the infrawatch database
db = db.getSiblingDB('infrawatch');

// Create collections with validation
db.createCollection('users', {
  validator: {
    $jsonSchema: {
      bsonType: 'object',
      required: ['email', 'username', 'hashed_password'],
      properties: {
        email: {
          bsonType: 'string',
          description: 'User email address'
        },
        username: {
          bsonType: 'string',
          description: 'Username'
        },
        hashed_password: {
          bsonType: 'string',
          description: 'Hashed password'
        }
      }
    }
  }
});

db.createCollection('metrics');
db.createCollection('logs');
db.createCollection('alerts');
db.createCollection('alert_rules');
db.createCollection('health_checks');
db.createCollection('log_stats');

// Create indexes
// Users
db.users.createIndex({ email: 1 }, { unique: true });
db.users.createIndex({ username: 1 }, { unique: true });

// Metrics
db.metrics.createIndex({ timestamp: -1 });
db.metrics.createIndex({ source: 1, timestamp: -1 });
db.metrics.createIndex({ metric_type: 1, timestamp: -1 });
db.metrics.createIndex({ namespace: 1, timestamp: -1 });
db.metrics.createIndex({ timestamp: 1 }, { expireAfterSeconds: 604800 }); // 7 days TTL

// Logs
db.logs.createIndex({ timestamp: -1 });
db.logs.createIndex({ level: 1, timestamp: -1 });
db.logs.createIndex({ source: 1, timestamp: -1 });
db.logs.createIndex({ message: 'text', source: 'text' });
db.logs.createIndex({ timestamp: 1 }, { expireAfterSeconds: 2592000 }); // 30 days TTL

// Alerts
db.alerts.createIndex({ created_at: -1 });
db.alerts.createIndex({ status: 1, created_at: -1 });
db.alerts.createIndex({ severity: 1, created_at: -1 });

// Alert Rules
db.alert_rules.createIndex({ name: 1 }, { unique: true });
db.alert_rules.createIndex({ enabled: 1 });
db.alert_rules.createIndex({ user_id: 1 });

print('MongoDB initialized successfully!');
