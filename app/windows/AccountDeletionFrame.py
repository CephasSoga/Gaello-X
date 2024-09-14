import os
import sys
import json
import asyncio
import aiohttp
from pathlib import Path
from typing import Callable

from PyQt5 import  uic
from PyQt5.QtWidgets import QFrame
from pymongo import MongoClient

from app.handlers.AuthHandler import sync_read_user_cred_file
from utils.appHelper import setRelativeToMainWindow, adjustForDPI, showWindow
from utils.paths import getFrozenPath, getFileSystemPath
from utils.envHandler import getenv
from utils.asyncJobs import asyncWrap, ThreadRun
from utils.databases  import mongoUpdate, mongoGet, mongoDeleteOne

# import resources
import app.config.resources

class AccountDeleteCompletion(QFrame):
    def __init__(self, parent=None):
        super(AccountDeleteCompletion, self).__init__(parent)
        path = getFrozenPath(os.path.join("assets", "UI", "accountDeletionComplete.ui"))
        if os.path.exists(path):
            uic.loadUi(path, self)
        else:
            raise FileNotFoundError(f"{path} not found")
        
        self.initUI()
        
    def initUI(self):
        adjustForDPI(self)
        self.connectSlots()

    def connectSlots(self):
        self.close_.clicked.connect(self.closeWholeApp)

    def connectSlots(self):
        self.close_.clicked.connect(self.closeWholeApp)

    def closeWholeApp(self):
        sys.exit(0)

class AccountDeleteTrigger(QFrame):
    def __init__(self, connection: MongoClient, parent=None):
        super(AccountDeleteTrigger, self).__init__(parent)
        path = getFrozenPath(os.path.join("assets", "UI", "accountDeletion.ui"))
        if os.path.exists(path):
            uic.loadUi(path, self)
        else:
            raise FileNotFoundError(f"{path} not found")
        
        self.connection = connection
        
        self.initUI()

    def initUI(self):
        adjustForDPI(self)
        self.setContents()
        self.connectSlots()

    def setContents(self):

        # get reasons why user is leaving
        service = "Poor service" if self.service.isChecked() else None
        model = "Poor model accuracy " if  self.model.isChecked() else None
        dataList = "Data not exhaustive enough" if self.dataList.isChecked() else None
        dataForm = "Near-realtime is not appropriate" if self.dataForm.isChecked() else None
        ui = "Poor UI responsiveness" if self.ui.isChecked() else None
        others = "Other reasons" if self.others.isChecked() else None
        features = "Poor features implementation" if  self.features.isChecked() else None

        othersText = self.othersLineEdit.text()

        self.reasonsDict = {
            "service": service,
            "model": model,
            "dataList": dataList,
            "dataForm": dataForm,
            "ui": ui,
            "others": others,
            "features": features,
            "othersText": othersText
        }


    def connectSlots(self):
        self.okButton.clicked.connect(lambda: asyncio.ensure_future(self.waitForDeletion()))
        self.cancelButton.clicked.connect(self.cancel)

    def cancel(self):
        self.close()
        return
    
    async def waitForDeletion(self):
        await self.deleteAccount()

    async def deleteAccount(self):
        if not getattr(self, 'reasonsDict', None):
            self.reasonsDict = {}

        # get user credentials
        userCreds: dict = await ThreadRun(sync_read_user_cred_file)
        userEmail = userCreds.get("email", "")
        # get user details
        asyncMongoGet = asyncWrap(mongoGet)
        usersInfo = await asyncMongoGet(database="UsersAuth", collection="users", limit=int(1e7), connection=self.connection)
        thisUser = [user for user in usersInfo if user['user']['email'] == userEmail]
        subscriptionId = thisUser[0].get("subscriptionId", None)
        acessToken = getenv("ACCESS_TOKEN")

        # make reasons string
        reason = json.dumps(self.reasonsDict, indent=4)

        if subscriptionId: # user is under some subscription plan
            # cancel subscription
            await self.cancelPlan(subscriptionId, acessToken, reason)

        # delete user from active users
        asyncMongoDel = asyncWrap(mongoDeleteOne)
        await asyncMongoDel(database="UsersAuth", collection="users", filter={"user.email": userEmail}, connection=self.connection)
        # delete user permanent creds file
        path = Path(
            getFileSystemPath(os.path.join(getenv("APP_BASE_PATH"), "credentials", "credentials.json"))
        )
        if path.exists():
            os.remove(path)
        # user goes in inactive users
        await ThreadRun(self.connection["UsersAuth"]["inactive_users"].insert_one, thisUser[0])
        asyncMongoUpdate = asyncWrap(mongoUpdate)
        await asyncMongoUpdate(database="UsersAuth", collection="inactive_users", query={"user.email": userEmail}, update={"$set": {"status": "INACTIVE", "reason": reason}}, connection=self.connection)

        # then show completion
        completion = AccountDeleteCompletion()
        setRelativeToMainWindow(completion, self.parent(), "center")


    async def cancelPlan(self, subscriptionId: str, accessToken: str, reason: str, mode: str = "live"):
        headers = {
        'Authorization': accessToken,
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        }

        data = { "reason": reason }

        # url = 'https://api-m.sandbox.paypal.com/v1/billing/subscriptions/I-BW452GLLEP1G/cancel'
        if mode == 'live':
            url = f'https://api-m.paypal.com/v1/billing/subscriptions/{subscriptionId}/cancel'
        elif mode == 'sandbox':
            url = f'https://api-m.sandbox.paypal.com/v1/billing/subscriptions/{subscriptionId}/cancel'
        

        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=data) as response:
                if response.status == 200:
                    response_data = await response.json()
                    print("Subscription canceled successfully:", response_data)
                else:
                    response_text = await response.text()
                    print(f"Failed to cancel subscription: {response.status} - {response_text}")
