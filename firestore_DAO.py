from firebase_admin import firestore, initialize_app
from datetime import datetime
from config import companyId

class FirestoreDAO:
    def __init__(self):
        initialize_app()
        self.__db = firestore.client()
        
# --------Member--------------
    def setMember(self, myMember):
        myMember['role'] = 'worker'
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
            "setMember": True
        }

    def updateMember(self, member):
        doc = self.__db.document(f"members/{member['id']}")
        doc.update(member)

    def getMembers(self, company) -> list:
        members = []
        if "companyId" in company.keys():
            docs = self.__db.collection(f"companies/{company['companyId']}/members").stream()
            for doc in docs:
                doc = self.__db.document(f"members/{doc.id}")
                members.append(doc.get().to_dict())
        else:
            doc = self.__db.collection('members').document(company["id"]).get()
            if doc.to_dict() != None:
                members.append(doc.to_dict())
        return members
    
    def addBeginOfWorkRecord(self, record, logger):
        if record is None:
            logger.info("record is None")
            return False;
        if record['date'] == "":
            logger.info("No date in record")
            return False;
        if self.getBeginOfWorkRecord(record['memberId']) is not None:
            logger.info("Already started work record in the past 20 hours")
            return False
        if self.getEndOfWorkRecord(record['memberId']):
            start = datetime.fromisoformat(self.getBeginOfWorkRecord(record['memberId']).to_dict()['date'][:-1])
            end = datetime.fromisoformat(self.getEndOfWorkRecord(record['memberId']).to_dict()['date'][:-1])
            logger.info(start)
            logger.info(end)
            if start >= end:
                logger.info("Didn't end work after starting work since last time")
                return False
        collection = self.__db.collection("beginOfWork")
        collection.add(record)
        return True
    
    #get the (only) record of the last 20 hours
    def getBeginOfWorkRecord(self, memberId):
        collection = self.__db.collection("beginOfWork")
        for doc in collection.stream():
            timeDelta = datetime.now() - datetime.fromisoformat(doc.to_dict()['date'][:-1]) #exclude the 'Z' in the end before formatting 
            if doc.to_dict()['memberId'] == memberId and timeDelta.seconds < 72000:
                return doc
        return None


    def addEndOfWorkRecord(self, record, logger):
        if record is None:
            logger.info("record is None")
            return False;
        if record['date'] == "":
            logger.info("No date in record")
            return False;
        if self.getBeginOfWorkRecord(record['memberId']) is None:
            logger.info("No start work record in 20 hours")
            return False
        if self.getEndOfWorkRecord(record['memberId']):
            start = datetime.fromisoformat(self.getBeginOfWorkRecord(record['memberId']).to_dict()['date'][:-1])
            end = datetime.fromisoformat(self.getEndOfWorkRecord(record['memberId']).to_dict()['date'][:-1])
            logger.info(start)
            logger.info(end)
            if start <= end:
                logger.info("Didn't start work after ending work since last time")
                return False
        collection = self.__db.collection("endOfWork")
        collection.add(record)
        return True

    #get the (only) record of the last 20 hours
    def getEndOfWorkRecord(self, memberId):
        collection = self.__db.collection("endOfWork")
        for doc in collection.stream():
            timeDelta = datetime.now() - datetime.fromisoformat(doc.to_dict()['date'][:-1]) 
            if doc.to_dict()['memberId'] == memberId and timeDelta.seconds < 72000:
                return doc
        return None