from firebase_admin import firestore, initialize_app
from datetime import datetime, timedelta
from config import companyId
import logging
import threading
from line_api import PushMessage

class FirestoreDAO:
    def __init__(self, logger=logging):
        initialize_app()
        self.__db = firestore.client()
        self.logger = logger

    def getCompanies(self, company=None) -> list:
        companies = []
        if company:
            doc = self.__db.document(f"companies/{company['companyId']}")
            companies.append(doc.get().to_dict())
        else:
            docs = self.__db.collection("companies").stream()
            siteIdOfName = {}
            for doc in docs:
                siteIdOfName[doc.id] = doc._data['name']
                companies.append({"id": doc.id, "name": doc.to_dict()['name']})
        return companies
        
# --------Member--------------
    def setMember(self, myMember, role='worker', salary=180):
        myMember['role'] = role
        myMember['salary'] = salary
        memberCollection = self.__db.collection("members")
        memberList = list(doc._data for doc in memberCollection.stream())
        for member in memberList:
            if member["lineId"] == myMember['lineId']:
                # check company has member
                for docs in self.__db.collection(f"companies/{companyId}/members").stream():
                    if docs.id == member['id']:
                        return member

                # create memberid in company
                self.__db.document(f"companies/{companyId}/members/{member['id']}").set(None)
                member["setMember"] = True
                return member

        # create member
        memberId = memberCollection.add(myMember)[1].id
        memberCollection.document(memberId).update({'id': memberId})

        # create member in company
        self.__db.document(f"companies/{companyId}/members/{memberId}").set(None)
        return {
            "name": myMember['name'],
            "lineId": myMember['lineId'],
            "id": memberId,
            "salary": myMember['salary'],
            "setMember": True
        }
    def addMember(self, myMember, role='worker', salary=180): # with firebase uid
        myMember['role'] = role
        myMember['salary'] = salary
        memberCollection = self.__db.collection("members")
        memberList = list(doc._data for doc in memberCollection.stream())
        for member in memberList:
            if member["lineId"] == myMember['lineId']:
                # check company has member
                for docs in self.__db.collection(f"companies/{companyId}/members").stream():
                    if docs.id == member['id']:
                        return member

                # create memberid in company
                self.__db.document(f"companies/{companyId}/members/{member['id']}").set(None)
                member["setMember"] = True
                return member

        # create member
        memberId = myMember['id']
        memberCollection.document(memberId).set(myMember)

        # create member in company
        self.__db.document(f"companies/{companyId}/members/{memberId}").set(None)
        return {
            "name": myMember['name'],
            "lineId": myMember['lineId'],
            "id": myMember['id'],
            "salary": myMember['salary'],
            "setMember": True
        }
    def updateMember(self, member):
        doc_ref = self.__db.document(f"members/{member['id']}")
        if doc_ref.get().exists:
            doc_ref.update(member)
            return True
        else:
            self.logger.info('ID NOT FOUND')
            return False

    def getMembers(self, company) -> list:
        members = []
        if "companyId" in company.keys():
            docs = self.__db.collection(f"companies/{company['companyId']}/members").stream()
            for doc in docs:
                doc = self.__db.document(f"members/{doc.id}")
                member = doc.get().to_dict()
                if member:
                    members.append(member)
        else:
            doc = self.__db.collection('members').document(company["id"]).get()
            if doc.to_dict() != None:
                members.append(doc.to_dict())
        return members
    
    def getMember(self, company, memberId):
        members = self.getMembers(company)
        for member in members:
            self.logger.info(f"{member['id']} vs {memberId}")
            if member['id'] == memberId:
                return member
        self.logger.info("ID NOT FOUND")
        return None

    
    def addBeginOfWorkRecord(self, record):
        if record is None:
            self.logger.info("record is None")
            return False
        if record['date'] == "":
            self.logger.info("No date in record")
            return False
        if self.getBeginOfWorkRecord(record['memberId']) is not None:
            self.logger.info("Already started work record in the past 20 hours")
            line = PushMessage()
            message = {
                "lineId": self.getMembers({'id': record['memberId']})[0]['lineId'],
                "messageType": "textTemplate",
                "content": "上班打卡失敗\n"
                "20小時內已經有上班的紀錄 我們是鼓勵正常作息的佛心公司\n"
                "╰(⊙д⊙)╮    ╭(⊙д⊙)╯"
            }
            notificationThread = threading.Thread(target=line.pushMessage, args=(message,))
            notificationThread.start()
            return False
        collection = self.__db.collection("beginOfWork")
        collection.add(record)
        line = PushMessage()
        message = {
            "lineId": self.getMembers({'id': record['memberId']})[0]['lineId'],
            "messageType": "textTemplate",
            "content": "上班打卡成功\n"
            "早安 人生最美的不是風景 而是每天快樂的心情🌞\n"
        }
        notificationThread = threading.Thread(target=line.pushMessage, args=(message,))
        notificationThread.start()
        return True
    
    #get the (only) record of the last 20 hours
    def getBeginOfWorkRecord(self, memberId):
        collection = self.__db.collection("beginOfWork")
        for doc in collection.stream():
            timeDelta = datetime.now() - datetime.fromisoformat(doc.to_dict()['date'][:-1]) #exclude the 'Z' in the end before formatting 
            if doc.to_dict()['memberId'] == memberId and timeDelta.total_seconds() < 72000:
                return doc
        return None


    def addEndOfWorkRecord(self, record):
        if record is None:
            self.logger.info("record is None")
            return False
        if record['date'] == "":
            self.logger.info("No date in record")
            return False
        if self.getBeginOfWorkRecord(record['memberId']) is None:
            self.logger.info("No start work record in 20 hours")
            line = PushMessage()
            message = {
                "lineId": self.getMembers({'id': record['memberId']})[0]['lineId'],
                "messageType": "textTemplate",
                "content": "下班打卡失敗\n"
                "20小時內無上班打卡記錄，沒上班怎麼下班🧐\n"
            }
            notificationThread = threading.Thread(target=line.pushMessage, args=(message,))
            notificationThread.start()
            return -1
        if self.getEndOfWorkRecord(record['memberId']):
            start = datetime.fromisoformat(self.getBeginOfWorkRecord(record['memberId']).to_dict()['date'][:-1])
            end = datetime.fromisoformat(self.getEndOfWorkRecord(record['memberId']).to_dict()['date'][:-1])
            self.logger.info(start)
            self.logger.info(end)
            if start <= end:
                self.logger.info("Didn't start work after ending work since last time")
                line = PushMessage()
                message = {
                    "lineId": self.getMembers({'id': record['memberId']})[0]['lineId'],
                    "messageType": "textTemplate",
                    "content": "下班打卡失敗\n"
                    "上次下班打卡後還沒上班打卡的紀錄喔😯\n"
                }
                notificationThread = threading.Thread(target=line.pushMessage, args=(message,))
                notificationThread.start()
                return -1
        collection = self.__db.collection("endOfWork")
        collection.add(record)
        start = datetime.fromisoformat(self.getBeginOfWorkRecord(record['memberId']).to_dict()['date'][:-1])
        end = datetime.fromisoformat(record['date'][:-1])
        workTime = (end - start).total_seconds()
        line = PushMessage()
        message = {
            "lineId": self.getMembers({'id': record['memberId']})[0]['lineId'],
            "messageType": "textTemplate",
            "content": "下班打卡成功\n"
            f"工作時間: {int(workTime // 60 // 60)} 小時 {int(workTime // 60 % 60)} 分鐘\n"
        }
        notificationThread = threading.Thread(target=line.pushMessage, args=(message,))
        notificationThread.start()
        return int(workTime)

    #get the (only) record of the last 20 hours
    def getEndOfWorkRecord(self, memberId):
        collection = self.__db.collection("endOfWork")
        for doc in collection.stream():
            timeDelta = datetime.now() - datetime.fromisoformat(doc.to_dict()['date'][:-1]) 
            if doc.to_dict()['memberId'] == memberId and timeDelta.total_seconds() < 72000:
                return doc
        return None

    def addDayOffRecord(self, record):
        collection = self.__db.collection("dayOff")
        collection.add(record)
        return True

    def getAttendenceRecords(self, memberId):
        collection = self.__db.collection("beginOfWork")
        beginOfWork = [doc.to_dict() for doc in collection.stream() if doc.to_dict()['memberId'] == memberId]
        collection = self.__db.collection("endOfWork")
        endOfWork = [doc.to_dict() for doc in collection.stream() if doc.to_dict()['memberId'] == memberId]
        collection = self.__db.collection("dayOff")
        dayOff = [doc.to_dict() for doc in collection.stream() if doc.to_dict()['memberId'] == memberId]
        return (beginOfWork, endOfWork, dayOff)