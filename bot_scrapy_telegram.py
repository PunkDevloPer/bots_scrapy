import json
import time
import requests
from bs4 import BeautifulSoup
import telebot


class ScrapyTelegramBot:
    def __init__(self, token, chat_id, report_id):
        self.bot = telebot.TeleBot(token)
        self.chat_id = chat_id
        self.report_id = report_id
        self.dictionary = {}
        self.sent_vulnerabilities = []
        self.sent_messages = []

    def handle_start(self, message):
        self.bot.send_message(
            message.chat.id, "Hola, ¿cuántas páginas desea generar?")
        self.bot.register_next_step_handler(message, self.handle_pages)

    def handle_pages(self, message):
        try:
            num_pages = int(message.text)
            self.generate_pages(num_pages)
            self.save_to_json_file("report.json")
            self.send_report("report.json")
        except ValueError:
            self.bot.send_message(
                message.chat.id, "Por favor, ingrese un número válido.")

    def generate_pages(self, num_pages):
        for i in range(num_pages):
            page = i
            URL = "https://www.incibe.es/incibe-cert/alerta-temprana/vulnerabilidades?"
            page = f"field_vul_product=&page={i}".format(i=page)
            URL = URL + page
            print(URL)
            time.sleep(4)

            try:
                response = requests.get(URL, timeout=10)
                response.raise_for_status()
            except requests.exceptions.RequestException as e:
                print("Error de conexión:", e)
                exit(1)

            soup = BeautifulSoup(response.content, "html.parser")
            soup.encode("utf-8")

            teasers = soup.find_all(
                class_="node-vulnerabilities-teaser contextual-region")

            for teaser in teasers:
                vuln_elem = teaser.find('h2', {'class': 'node-title'})
                date_elem = teaser.find(
                    'div', {'class': 'field-publication-date'})
                severity_elem = teaser.find(
                    'div', {'class': 'field-vulnerability-severity-text'})
                description_elem = teaser.find(
                    'div', {'class': 'field-description'})

                links = teaser.find_all('a')
                hrefs = [link.get('href')
                         for link in links if link.get('href')]

                if vuln_elem and date_elem and severity_elem and description_elem:
                    self.dictionary[vuln_elem.text] = {
                        'vuln': vuln_elem.text,
                        'date': date_elem.text.strip("\n"),
                        'severity': severity_elem.text,
                        'description': description_elem.text,
                        'links': "https://www.incibe.es" + hrefs[0]
                    }

    def save_to_json_file(self, vuln_file_path):
        dic = self.dictionary
        json_string = json.dumps(
            dic, indent=4, sort_keys=True, ensure_ascii=False)
        json_string = json_string.replace("***", "-")
        with open(vuln_file_path, 'w', encoding='utf-8') as f:
            f.write(json_string)

    def send_report(self, vuln_file_path):
        with open(vuln_file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        for item in data.values():
            if item['vuln'] not in self.sent_vulnerabilities:
                if item['vuln'] not in self.sent_messages:
                    # Si la vulnerabilidad no ha sido enviada, enviar el mensaje
                    message = f"<b>Vulnerabilidad:</b> {item['vuln']}\n"
                    message += f" {item['date']}\n"
                    message += f"<b>Enlace:</b> {item['links']}"
                    self.bot.send_message(
                        self.chat_id, message, parse_mode='HTML')
                    # Agregar la vulnerabilidad a la lista de vulnerabilidades enviadas
                    self.sent_vulnerabilities.append(item['vuln'])
                    # Agregar el mensaje a la lista de mensajes enviados
                    self.sent_messages.append(item['vuln'])
                    # Guardar el estado actualizado de los mensajes enviados en el archivo JSON
                    self.save_sent_messages()

                    time.sleep(5)

    def save_sent_messages(self):
        with open("sent_messages.json", 'w', encoding='utf-8') as f:
            json.dump(self.sent_messages, f)

    def load_sent_messages(self):
        try:
            with open("sent_messages.json", 'r', encoding='utf-8') as f:
                self.sent_messages = json.load(f)
        except FileNotFoundError:
            self.sent_messages = []

    def check_message_sent(self):
        file_message_path = "file_message_path.json"
        try:
            with open(file_message_path, 'r', encoding='utf-8') as f:
                file_message_path = json.load(f)
        except FileNotFoundError:
            file_message_path = []


if __name__ == '__main__':
    bot = ScrapyTelegramBot(
        token=(""), #your token here 
        chat_id=-, #your chat id here
        report_id= # your chat group here
    )
    bot.generate_pages(2) #-> here numb of pages 
    bot.save_to_json_file("report.json")
    bot.send_report("report.json")
