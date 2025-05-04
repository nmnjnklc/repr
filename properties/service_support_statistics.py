properties: dict = {
    "apps": {
        "app_1": {
            "connection": {"database": "app1", "host": "1.2.3.4", "user": "user1", "password": "password1"},
            "accounts": ["account1@company.com"]
        },
        "app_2": {
            "connection": {"database": "app2", "host": "5.6.7.8", "user": "user2", "password": "password2"},
            "accounts": ["account2@company.com", "account3@company.com"]
        },
        "app_3": {
            "connection": {"database": "app3", "host": "4.3.2.1", "user": "user3", "password": "password3"},
            "accounts": ["account4@company.com", "account5@company.com"]
        }
    },
    "mail_to": ["person1@company.com", "person2@company.com"]
}