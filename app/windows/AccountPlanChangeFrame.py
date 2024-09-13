import os
import time
import asyncio
import aiohttp
from pathlib import Path
from typing import Callable

from PyQt5 import  uic
from PyQt5.QtCore import QEvent, Qt
from PyQt5.QtWidgets import QFrame
from pymongo import MongoClient

from app.windows.MessageBox import MessageBox
from app.windows.PaymentForm import PaymentForm
from app.handlers.AuthHandler import sync_read_user_cred_file
from app.windows.NewAccountPlan import NewAccountPlan
from app.windows.NewAccountOk import AccountAllSet, AccountInitFailure
from app.windows.NewAccountPlan import NewAccountPlan
from app.windows.Styles import msgBoxStyleSheet 
from utils.appHelper import setRelativeToMainWindow, adjustForDPI, showWindow
from utils.paths import getFrozenPath
from utils.envHandler import getenv
from utils.asyncJobs import asyncWrap, ThreadRun
from utils.databases  import mongoGet, mongoUpdate


class UpgradePaymentForm(PaymentForm):
    def __init__(self, connection: MongoClient, nodeAppPath: Path | str, execPath: Path | str = ".", parent=None):
        super(UpgradePaymentForm, self).__init__(connection=connection, nodeAppPath=nodeAppPath, execPath=execPath,parent=parent)
    
    # override method
    def spawnTerminated(self):
        if self.validatePayment():
            parent = self.parent()
            allSet = AccountAllSet()
            allSet.label.SetText("Your account has been upgraded!") # The change is here
            allSet.hide()
            setRelativeToMainWindow(allSet, parent, 'center')
            self.close()
        else:
            self.renderFailure()

    # override method
    def renderFailure(self):
        parent = self.parent()
        paymentFailed = AccountInitFailure()
        paymentFailed.label.SetText("Payment failed. Please try again.") # The change is here
        paymentFailed.hide()
        setRelativeToMainWindow(paymentFailed, parent, 'center')
        self.close()

class AccountUpgradeFromFree(NewAccountPlan):
    def __init__(self, connection: MongoClient, parent=None):
        super(AccountUpgradeFromFree, self).__init__(connection=connection, parent=parent)
        self.connection = connection

    # override method
    def submitStandardTier(self):
        parent = self.parent()
        nodeAppPath = getFrozenPath(os.path.join('assets', 'binaries', 'checkouts','standard', 'Gaello-webpaypal-standard-tier.exe'))
        execPath = getFrozenPath(".")
        self.paymentForm = UpgradePaymentForm(connection=self.connection, nodeAppPath=nodeAppPath, execPath=execPath) # The change is here
        if self.paymentForm:
            self.paymentForm.hide()
            if parent:
                setRelativeToMainWindow(self.paymentForm, parent, 'center')
            else:
                self.paymentForm.show()
            self.hide()

    # override method
    def submitAdvancedTier(self):
        parent = self.parent()
        nodeAppPath = getFrozenPath(os.path.join('assets', 'binaries', 'checkouts','advanced', 'Gaello-webpaypal-advanced-tier.exe'))
        execPath = getFrozenPath(".")
        self.paymentForm = UpgradePaymentForm(connection=self.connection, nodeAppPath=nodeAppPath, execPath=execPath) # The change is here
        if self.paymentForm:
            self.paymentForm.hide()
            if parent:
                setRelativeToMainWindow(self.paymentForm, parent, 'center')
            else:
                self.paymentForm.show()
            self.hide()


class AccountPlanChange(QFrame):
    def __init__(self, connection: MongoClient, parent=None):
        super(AccountPlanChange, self).__init__(parent)
        path = getFrozenPath(os.path.join("assets", "UI", "accountPlanChange.ui"))
        if os.path.exists(path):
            uic.loadUi(path, self)
        else:
            raise FileNotFoundError(f"{path} not found")

        self.connection = connection
        self.dbName = "UsersAuth"
        self.collection = "users"

        self.initUI()

    def initUI(self):
        adjustForDPI(self)
        self.connectSlots()

    def connectSlots(self):
        self.standardTierButton.clicked.connect(lambda: asyncio.ensure_future(self.waitForStantardTierTask()))
        self.advancedTierButton.clicked.connect(lambda: asyncio.ensure_future(self.waitForAdvancedTierTask()))
        self.close_.clicked.connect(self.close)


    async def waitForStantardTierTask(self):
        await self.proceedForStandard()

    async def waitForAdvancedTierTask(self):
        await self.proceedForAdvanced()
    
    async def proceedForStandard(self):
        messageBox = MessageBox()
        userCreds: dict = await ThreadRun(sync_read_user_cred_file)
        userEmail = userCreds.get("email", "")
        if not userEmail:
            messageBox.level("critical")
            messageBox.title("Critical: Credentials Error.")
            messageBox.message("Please login to proceed.")
            messageBox.buttons(("ok",))
            messageBox.exec_()
            return
        
        asyncMongoGet = asyncWrap(mongoGet)
        usersInfo = await asyncMongoGet(database="UsersAuth", collection="users", limit=int(1e7), connection=self.connection)
        thisUser = [user for user in usersInfo if user['user']['email'] == userEmail]
        subscriptionId = thisUser[0].get("subscriptionId", None)
        userLevel = thisUser[0].get("userLevel", 0)
        acessToken = getenv("ACCESS_TOKEN")
        if not subscriptionId or userLevel == 0:
            # User is on free tier
            messageBox.level("information")
            messageBox.title("Web payment form")
            messageBox.message("A Web payment form will be opened  in your default browser. Please add your payment method and complete the payment.")
            messageBox.buttons(("ok", "cancel"))
            result = messageBox.exec_()
            if result == messageBox.Ok:
                accountPlan = AccountUpgradeFromFree(connection=self.connection, parent=self)
                accountPlan.submitStandardTier()
                self.hide()
                return
            else:
                self.close()
                return

        elif userEmail and userLevel > 0 and subscriptionId and acessToken:
            messageBox.level("question")
            messageBox.title("Accont Plan Change")
            messageBox.message("Are you sure you want to change your plan to Standard Tier?")
            messageBox.buttons(("yes", "no"))
            result = messageBox.exec_()
            if result == messageBox.Yes:
                await self.toStandardTier(userEmail,userLevel, subscriptionId, acessToken)
                return
            elif result == messageBox.No:
                self.close()
                return
            else:
                return

        else:
            messageBox.level("warning")
            messageBox.title("Warning: Plan Change")
            messageBox.message("We could not proceess your request. Please try again.")
            messageBox.buttons(("ok",))
            messageBox.exec_()
            self.close()
            
    async def proceedForAdvanced(self):
        messageBox = MessageBox()
        userCreds: dict = await ThreadRun(sync_read_user_cred_file)
        userEmail = userCreds.get("email", "")
        if not userEmail:
            messageBox.level("critical")
            messageBox.title("Critical: Credentials Error.")
            messageBox.message("Please login to proceed.")
            messageBox.buttons(("ok",))
            messageBox.exec_()
            return
        
        asyncMongoGet = asyncWrap(mongoGet)
        usersInfo = await asyncMongoGet(database="UsersAuth", collection="users", limit=int(1e7), connection=self.connection)
        thisUser = [user for user in usersInfo if user['user']['email'] == userEmail]
        subscriptionId = thisUser[0].get("subscriptionId", None)
        userLevel = thisUser[0].get("userLevel", 0)
        acessToken = getenv("ACCESS_TOKEN")
        if not subscriptionId or userLevel == 0:
           # User is on free tier
            messageBox.level("information")
            messageBox.title("Web payment form")
            messageBox.message("A Web payment form will be opened  in your default browser. Please add your payment method and complete the payment.")
            messageBox.buttons(("ok", "cancel"))
            result = messageBox.exec_()
            if result == messageBox.Ok:
                accountPlan = AccountUpgradeFromFree(connection=self.connection, parent=self)
                accountPlan.submitAdvancedTier()
                self.hide()
                return
            else:
                self.close()
                return

        elif userEmail and userLevel > 0 and subscriptionId and acessToken:
            messageBox.level("question")
            messageBox.title("Accont Plan Change")
            messageBox.message("Are you sure you want to change your plan to Advanced Tier?")
            messageBox.buttons(("yes", "no"))
            result = messageBox.exec_()
            if result == messageBox.Yes:
                await self.toAdvancedTier(userEmail, userLevel, subscriptionId, acessToken)
                return
            elif result == messageBox.No:
                self.close()
                return
            else:
                return
        else:
            messageBox.level("warning")
            messageBox.title("Warning: Plan Change")
            messageBox.message("We could not proceess your request. Please try again.")
            messageBox.buttons(("ok",))
            messageBox.exec_()
            self.close()
    
    async def toStandardTier(self, email: str, userLevel: int, subscriptionId: str, accessToken: str, mode: str = "live"):
        if userLevel == 2:
            messageBox = MessageBox()
            messageBox.level("warning")
            messageBox.title("Warning")
            messageBox.message("You are already on Standard Tier.")
            messageBox.buttons(("ok",))
            messageBox.exec_()
        else:
            planId  = getenv("STANDARD_PLAN_ID")
            await self.upadateOrDowngradePlanWithNoFail(subscriptionId, planId, accessToken, mode)
            await self.updateUser(email, "standard", 2)

    async def toAdvancedTier(self, email: str, userLevel: int, subscriptionId: str, accessToken: str, mode: str = "live"):
        if userLevel == 3:
            messageBox = MessageBox()
            messageBox.level("warning")
            messageBox.title("Warning")
            messageBox.message("You are already on Advanced Tier.")
            messageBox.buttons(("ok",))
            messageBox.exec_()
        else:
            planId  = getenv("ADVANCED_PLAN_ID")
            await self.upadateOrDowngradePlanWithNoFail(subscriptionId, planId, accessToken, mode)
            await self.updateUser(email, "advanced", 3)

    async def upadateOrDowngradePlanWithNoFail(self, subscriptionId: str, newPlanId: str, accessToken: str, mode: str = "live"):
        try:
            _ = await self.upgradeOrDowngradePlan(subscriptionId, newPlanId, accessToken, mode)
            ok = AccountAllSet(self.parent())
            ok.label.setText("You have succesfully changed your plan!")
            showWindow(ok)
            self.close()
        except Exception as e:
            notOk = AccountInitFailure(self.parent())
            notOk.label.setText("Failed to change plan. Please try again later.")
            showWindow(notOk)
            self.close()


    async def changePlan(self, subscriptionId: str, newPlanId: str, accessToken: str, mode: str = "live"):
         # Define the base URLs for the PayPal API
        base_urls = {
            'sandbox': 'https://api-m.sandbox.paypal.com',
            'live': 'https://api-m.paypal.com'
        }

        # Determine the base URL based on the mode
        if mode == 'sandbox':
            base_url = base_urls['sandbox']
        elif mode == 'live':
            base_url = base_urls['live']
        else:
            raise ValueError("Wrong mode string. mode should be one of `'sandbox'` or `live`")

        # Construct the API URL
        url = f'{base_url}/v1/billing/subscriptions/{subscriptionId}/revise'

        # Define the request headers and body
        headers = {
            "Authorization": f"Bearer {accessToken}",
            'Content-Type': 'application/json',
        }
        body = {"plan_id": newPlanId}

        try:
            # Send the POST request asynchronously
            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=headers, json=body) as response:
                    # Raise an exception if the response status code is not 200 or 201
                    if response.status not in [200, 201]:
                        response_text = await response.text()
                        raise Exception(f"API request failed with status {response.status}: {response_text}")

                    # Optionally return the response if needed
                    return await response.json()

        except aiohttp.ClientError as e:
            raise Exception(f"API request failed: {e}")
        
    async def updateUser(self, email, subscription: str, authorizationLevel: int):
        asyncMongoUpdate = asyncWrap(mongoUpdate)
        _ = await asyncMongoUpdate(
            database=self.dbName, 
            collection=self.collection,
            connection=self.connection,  
            query={"user.email": email}, 
            update={"$set": {
                        "status": "ACTIVE", 
                        "subscription": subscription, 
                        "authorizationLevel": authorizationLevel
                        }
                    })