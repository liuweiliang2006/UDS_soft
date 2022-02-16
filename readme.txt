完成python版本的测试，使用原厂的驱动即可。使用的文件目录：\CAN分析仪资料20210714\二次开发库文件\x64
python使用3.8.0 64位版本

------------------------------------------------------------------------------------------------------------------------
为满足多帧数据的接收要求，更改了ISOTP模块的 protocol.py 文件，接收测试OK

   def process(self):
        """
        Function to be called periodically, as fast as possible. 
        This function is non-blocking.
        """	

        self.check_timeouts_rx()

        msg = True
        while msg is not None:
            msg = self.rxfn()
            if msg is not None:
                # print(msg)
                for zlgmsg in msg:
                    msgs = CanMessage(arbitration_id=zlgmsg.ID, data=zlgmsg.Data, dlc=zlgmsg.DataLen,extended_id=False)
                # self.logger.debug("Receiving :  (%d)\t %s" % (msgs.arbitration_id, len(msgs.data), binascii.hexlify(msgs.data)))
                    print("rec:id-%d,dlc-%d,data-%s" % (msgs.arbitration_id,msgs.dlc, binascii.hexlify(msgs.data)))
                    self.process_rx(msgs)
            # if msg is not None:
            #     self.logger.debug("Receiving : <%03X> (%d)\t %s" % (msg[0].arbitration_id, len(msg[0].data), binascii.hexlify(msg[0].data)))
            #     self.process_rx(msg)

        msg = True
        while msg is not None:
            msg = self.process_tx()
            if msg is not None:
                self.logger.debug("Sending : <%03X> (%d)\t %s" % (msg.arbitration_id, len(msg.data), binascii.hexlify(msg.data)))
                self.txfn(msg)
------------------------------------------------------------------------------------------------------------------------

https://github.com/pylessard/python-udsoncan
https://github.com/pylessard/python-can-isotp

…or create a new repository on the command line
echo "# UDS_soft" >> README.md
git init
git add README.md
git commit -m "first commit"
git branch -M main
git remote add origin git@github.com:liuweiliang2006/UDS_soft.git
git push -u origin main
…or push an existing repository from the command line
git remote add origin git@github.com:liuweiliang2006/UDS_soft.git
git branch -M main
git push -u origin main
…or import code from another repository
You can initialize this repository with code from a Subversion, Mercurial, or TFS project.

