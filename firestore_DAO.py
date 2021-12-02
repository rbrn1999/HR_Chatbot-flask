# from firebase_admin import firestore, initialize_app
# from config import companyId

# class FirestoreDAO:
#     def __init__(self):
#         initialize_app()
#         self.__db = firestore.client()
        
# # --------Member--------------
#     def setMember(self, myMember):
#         myMember['role'] = 'customer'
#         memberCollection = self.__db.collection("members")
#         memberList = list(doc._data for doc in memberCollection.stream())
#         for member in memberList:
#             if member["lineId"] == myMember['lineId']:
#                 # check company has member
#                 for docs in self.__db.collection(f"companies/{companyId}/members").stream():
#                     if docs.id == member['id']:
#                         return member

#                 # create memberid in company
#                 self.__db.document(f"companies/{companyId}/members/{member['id']}").set(None)
#                 member["setMember"] = True
#                 return member

#         # create member
#         memberId = memberCollection.add(myMember)[1].id
#         memberCollection.document(memberId).update({'id': memberId})

#         # create member in company
#         self.__db.document(f"companies/{companyId}/members/{memberId}").set(None)
#         return {
#             "name": myMember['name'],
#             "lineId": myMember['lineId'],
#             "id": memberId,
#             "setMember": True
#         }

#     def updateMember(self, member):
#         doc = self.__db.document(f"members/{member['id']}")
#         doc.update(member)

#     def getMembers(self, company) -> list:
#         members = []
#         if "companyId" in company.keys():
#             docs = self.__db.collection(f"companies/{company['companyId']}/members").stream()
#             for doc in docs:
#                 doc = self.__db.document(f"members/{doc.id}")
#                 members.append(doc.get().to_dict())
#         else:
#             doc = self.__db.collection('members').document(company["id"]).get()
#             if doc.to_dict() != None:
#                 members.append(doc.to_dict())
#         return members
