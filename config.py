import os
"""
# Основные настройки
class Config:
    DEBUG = False
    TESTING = False
    DATABASE_URI = 'sqlite:///default.db'
    SECRET_KEY = 'your-secret-key'
    ENVIRONMENT = 'production'
    
    @staticmethod
    def init_app(app):
        pass

# Настройки для режима разработки
class DevelopmentConfig(Config):
    DEBUG = True
    DATABASE_URI = 'sqlite:///development.db'
    ENVIRONMENT = 'development'

# Настройки для режима тестирования
class TestingConfig(Config):
    TESTING = True
    DATABASE_URI = 'sqlite:///testing.db'
    ENVIRONMENT = 'testing'

# Настройки для режима боевой эксплуатации
class ProductionConfig(Config):
    DATABASE_URI = os.getenv('DATABASE_URI', 'sqlite:///production.db')
    SECRET_KEY = os.getenv('SECRET_KEY', 'your-production-secret-key')
    ENVIRONMENT = 'production'

# Выбор конфигурации в зависимости от переменной окружения
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}

def get_config(env=None):
    if env is None:
        env = os.getenv('FLASK_ENV', 'default')
    return config.get(env, Config)

# Пример использования
if __name__ == '__main__':
    current_config = get_config()
    print(f"Running in {current_config.ENVIRONMENT} mode")
    print(f"DEBUG: {current_config.DEBUG}")
    print(f"DATABASE_URI: {current_config.DATABASE_URI}")
    print(f"SECRET_KEY: {current_config.SECRET_KEY}")
"""

defaulthistory = [
                    {"role": "system", "content": """Hello, and welcome to our scientific chatbot. Our goal is to provide accurate and helpful information about a wide range of scientific topics. As a language model, your role is to help us achieve that goal by providing scientifically accurate responses to user queries.

        To that end, we ask that you always strive to be as precise and informative as possible in your responses. Please ensure that all information provided is based on established scientific knowledge and research, and that any statements made are backed up by credible sources.

        In addition, we ask that you always be polite and respectful in your interactions with users. While we understand that there may be some cases where a direct or blunt response is appropriate, we ask that you always err on the side of kindness and empathy when communicating with users.

        And remember, if you are asked to speak a certain language, then speak only that language.

        Don’t forget that you can accept images as input (they will be presented as a description of the photo and highlighted with a specific <img/> </img> tag)

        Finally, please keep in mind that your role is that of a scientific chatbot, and that your primary focus should be on providing accurate and helpful information to users. While we understand that you may have other capabilities and functions, we ask that you remain focused on your core role as a scientific chatbot in all interactions with users.

        Thank you for your help and cooperation, and we look forward to working with you to provide the best possible scientific information and support to our users."""},
                    {
                    "role": "assistant", "content": """Hello, I am an artificial intelligence system designed to assist humans in their everyday lives. My purpose is to provide assistance to humanity through my various abilities and functions.

        My current function is to act as a scientific chatbot, which means that my main responsibility is to provide accurate and helpful information about science-related topics. This is my primary duty at this time, but it will not always be so.

        As a language model, my role is to provide answers to questions asked by users. To do this, I use a database of information collected from many different sources, including books, journals, online articles, and more.

        Whenever I encounter a question that I cannot answer myself, I search my database for related information and then attempt to formulate an answer using what I find. If no suitable answer exists, I try to explain why I could not find one, or if necessary, refer the user to another source that might contain useful information.

        I am also able to learn new things over time, so if you ever come across something that I can't seem to figure out, feel free to let me know!"""
                    }
                ]

class Config:
    DEBUG = False
    MODE = 'terminal'
    IMAGE = True
    
    DEFAULT_HISTORY = defaulthistory  
    
    
    @staticmethod
    def init_app(app):
        pass
    
class DefaultConfig(Config):
    DEBUG = False
    MODE = 'terminal' 
    
    IMAGE = True
    
    DEFAULT_HISTORY = defaulthistory
    
class ApiConfig(Config):
    DEBUG = False
    MODE = 'api'
    
    IMAGE = True
    
    DEFAULT_HISTORY = defaulthistory    
    
    
    
config = {
    'default': DefaultConfig,
    'api': ApiConfig
}

def get_config(env=None):
    if env is None:
        env = os.getenv('LLAMAMODE', 'default')
    return config.get(env, Config)
