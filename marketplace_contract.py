from pyteal import *
#product creation
#pyteal takes integers or byte slices
class Product:
    class Variables:
        name = Bytes("NAME")
        image = Bytes("IMAGE")
        description = Bytes("DESCRIPTION")
        price = Bytes("PRICE")
        sold = Bytes("SOLD")

    class AppMethods:
        buy = Bytes("buy")
    def application_creation(self):
        return Seq([
            Assert(Txn.application_args.length() == Int(4)),
            Assert(Txn.note() == Bytes("tutorial-marketplace:uv1")),
            Assert(Btoi(Txn.application_args[3]) > Int(0)),
            App.globalPut(self.Variables.name, Txn.application_args[0]),
            App.globalPut(self.Variables.image, Txn.application_args[1]),
            App.globalPut(self.Variables.description, Txn.application_args[2]),
            App.globalPut(self.Variables.price, Btoi(Txn.application_args[3])),
            App.globalPut(self.Variables.sold, Int(0)),
            Approve()
        ])
        #buy product interaction method.
        #contract payment and call methods grouped together.
    def buy(self):
        count = Txn.application_args[1]
        valid_number_of_transactions = Global.group_size() == Int(2)#number of transactions must be exactly 2.

        valid_payment_to_seller = And(
            Gtxn[1].type_enum() == TxnType.Payment,#payment.
            Gtxn[1].receiver() == Global.creator_address(),#receiver of payment is the app creator
            Gtxn[1].amount() == App.globalGet(self.Variables.price) * Btoi(count),
            Gtxn[1].sender() == Gtxn[0].sender(),
            )

        can_buy = And(valid_number_of_transactions,
                        valid_payment_to_seller)

        update_state = Seq([
            App.globalPut(self.Variables.sold, App.globalGet(self.Variables.sold) + Btoi(count)),
            Approve()
        ])

        return If(can_buy).Then(update_state).Else(Reject())  
    def application_deletion(self):
        return Return(Txn.sender() == Global.creator_address()) 
        
        #check transaction conditions loop
    def application_start(self):
        return Cond(
            [Txn.application_id() == Int(0), self.application_creation()],#create app if app id = 0
            [Txn.on_completion() == OnComplete.DeleteApplication, self.application_deletion()],#check if app deletion condition met and call the function
            [Txn.application_args[0] == self.AppMethods.buy, self.buy()]#default case
        )
        #The approval program is responsible for implementing most of the logic of an application.
        #Like smart signatures, this program will succeed only if one nonzero value is left on the stack upon program completion.
    def approval_program(self):
        return self.application_start()
        #remove smart contract from accounts balance methods
    def clear_program(self):
        return Return(Int(1))