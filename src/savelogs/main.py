import os
from datetime import datetime
from zipfile import ZipFile
import wx


def saveFiles():
    result = []
    '''
    make sure the save directory exists, create it if it doesn't
    '''
    path = os.path.join(os.getcwd(), "saveout")
    if not os.path.exists(path):
        os.makedirs(path)  
    
    
    '''
    create a save file name based on time of day
    '''
    now = datetime.now() # current date and time
    
    date_time = now.strftime("%Y%m%d_%H%M%S")
    
    fqn = os.path.join(path, date_time + ".zip") 
    result.append("saving output and logs to %s" % fqn) 
    
    dirs = [
        [ "output", os.path.join(os.getcwd(), "output") ],
        [ "logs",   os.path.join(os.getcwd(), "logs") ],
    ]
    
    with ZipFile(fqn, 'w') as zfp:
        for tag, sdir in dirs:
            result.append("processing directory %s" % sdir)
            try:
                fl = [ os.path.join(sdir, f) for f in os.listdir(sdir) if os.path.isfile(os.path.join(sdir, f))]
            except FileNotFoundError:
                fl = []
                
            for fn in fl:
                result.append("   file: %s" % fn)
                arcname = os.path.join(tag, os.path.basename(fn))
                zfp.write(fn, arcname = arcname)
                
    result.append("Completed...\n\n")
    result.append("Output File: %s" % fqn) 
    return result


class MainFrame(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, None, style=wx.DEFAULT_FRAME_STYLE)
        self.SetTitle("PSRY Suite Save Logs and Output")
        self.Bind(wx.EVT_CLOSE, self.OnClose)
        
        text = saveFiles()
        tcResult = wx.TextCtrl(self, wx.ID_ANY, "\n".join(text), size=(500, 500), style=wx.TE_MULTILINE | wx.TE_READONLY)
        
        hsz = wx.BoxSizer(wx.HORIZONTAL)
        hsz.AddSpacer(20)
        hsz.Add(tcResult)
        hsz.AddSpacer(20)
        
        vsz = wx.BoxSizer(wx.VERTICAL)
        vsz.AddSpacer(20)
        vsz.Add(hsz)
        vsz.AddSpacer(20)
        
        self.SetSizer(vsz)
        self.Layout()
        self.Fit()
        
    def OnClose(self, _):
        self.Destroy()
         

class App(wx.App):
    def OnInit(self):
        self.frame = MainFrame()
        self.frame.Show()
        return True


app = App(False)
app.MainLoop()

