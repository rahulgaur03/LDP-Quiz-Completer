from flaskwebgui import FlaskUI
from flask import Flask, render_template, request, jsonify
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys 
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time
import random

RunningStatus = "Ensure you're signed into Browser."

app = Flask(__name__)

@app.route("/")
def index():
    return render_template('index.html')

@app.route("/progress" , methods=['GET'])
def progress():
    data = { 
            "RunningStatus" : RunningStatus, 
        } 
  
    return jsonify(data) 

@app.route("/execute" , methods=['GET', 'POST'])
def execute():
    QuizURL = request.form.get('quizurl')
    Option = request.form.get('option') 
    FillValue = str(request.form.get('fillvalue')  if Option in ["a", "b"] else 0)
    chrome_options = Options()
    chrome_options.add_argument(f"user-data-dir=/tmp/myprofile")
    if Option != "a":
        ChatGPTPage = webdriver.Firefox()
        ChatGPTPage.get("https://chatgpt.com/")
    driver = webdriver.Chrome(options=chrome_options)
    driver.get(QuizURL)

    def ClickScrollButton(ChatGPTPage):
        try:
            scroll_button = WebDriverWait(ChatGPTPage, 2).until(EC.presence_of_element_located((By.CSS_SELECTOR, ".icon-md m-1 text-token-text-primary")))
            scroll_button.click()
        except Exception as e:
            pass

    def GetAnswerFromChatGPT(driver, Question = "Hi", Weightage = "1"):
        ClickScrollButton(driver)
        textarea = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "#prompt-textarea")))
        textarea.click()
        textarea.send_keys(f"This is my question:\n\n{Question} \n\nNow, provide only {Weightage} correct answers; do not include additional answers. Ensure the answers are in comma-separated format, like this:\n1\nor\n1,2\nor\n1,3,4\nEnsure that you include exactly {Weightage} correct answers, no less and no more.")
        textarea.send_keys(Keys.ENTER)

        WebDriverWait(driver, 50).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'button[data-testid="send-button"]')))
        ClickScrollButton(driver) 
        message = WebDriverWait(driver, 50).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".flex.flex-grow.flex-col.max-w-full > div")))[-1].text
        return message

    global RunningStatus
    ModuleTabs = WebDriverWait(driver, 60).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, '.MuiTabs-flexContainer.MuiTabs-flexContainerVertical button.MuiButtonBase-root')))
    MainContainer = WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.CSS_SELECTOR, '.MuiContainer-root.MuiContainer-maxWidthMd')))

    for Module in ModuleTabs:
        Module.click()
        AllProblems = MainContainer.find_elements(By.CSS_SELECTOR, '.MuiBox-root.css-1d823mq')
        for Problem in AllProblems:
            Problem_Statement_No = Problem.find_element(By.CSS_SELECTOR, '.MuiTypography-root.MuiTypography-h5').text
            Weightage = Problem.find_elements(By.CSS_SELECTOR, '.MuiTypography-root.MuiTypography-subtitle2')[0].text.split()[-1].strip()
            Status = Problem.find_elements(By.CSS_SELECTOR, '.MuiTypography-root.MuiTypography-subtitle2')[1].text.split()[-1].strip()
            Question = Problem.find_element(By.CSS_SELECTOR, '.MuiBox-root.css-t2nzj2').text
            AnswerBox = Problem.find_element(By.CSS_SELECTOR, '.MuiFormControl-root .MuiInputBase-input')
            RunningStatus = f"Currently Running: {Problem_Statement_No}"
            if Status in ["Unattempted", "Failed"]:
                if Option == "a":
                    AnswerValue = FillValue
                elif Option =="b":
                    AnswerValue = FillValue if Weightage == "1" else GetAnswerFromChatGPT(ChatGPTPage, Question, Weightage)
                elif Option == "c":
                    AnswerValue = GetAnswerFromChatGPT(ChatGPTPage, Question, Weightage)
                AnswerBox.send_keys(AnswerValue)
    RunningStatus = "All questions are solved."
    time.sleep(1)
    submit_button = WebDriverWait(driver, 60).until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'button.MuiButtonBase-root.MuiFab-root.MuiFab-extended.MuiFab-sizeMedium.MuiFab-info')))
    submit_button.click()
    RunningStatus = "Questions submitted. Closing browser soon."
    time.sleep(10)
    driver.quit()
    if Option != "a":
        ChatGPTPage.quit()
    RunningStatus = "Love ya 😘, gotta fly!!!"
    time.sleep(2)
    return "Bye bye, Please close app.!!!"

if __name__ == '__main__':  
    port = random.randint(1000, 9999)
    FlaskUI(app=app, server="flask",width=1200, height=800, port=port).run()



# pyinstaller --onefile --noconsole --icon=C:\Users\RahulGaurMAQSoftware\Desktop\Temp\ldp.jpg LDPQuizCompleter.py --add-data "static;static" --add-data "templates;templates"
# pyinstaller --onefile --noconsole LDPQuizCompleter.py --add-data "static;static" --add-data "templates;templates"
