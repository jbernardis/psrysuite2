import wx
import os
import json
import logging
from traineditor.trains.schedule import Schedule
from dispatcher.choicedlgs import ChooseSnapshotDlg

BTNSZ = wx.Size(120, 46)
wildcardJson = "JSON file (*.json)|*.json|"	 \
				"All files (*.*)|*.*"


class ChooseTrainsDlg(wx.Dialog):
	def __init__(self, parent, alltrains, rrserver, traincardsreport, schedulereport):
		wx.Dialog.__init__(self, parent, wx.ID_ANY, "")
		self.trainCardsReport = traincardsreport
		self.scheduleReport = schedulereport
		self.RRServer = rrserver
		self.Bind(wx.EVT_CLOSE, self.onClose)
		
		self.titleString = "Manage Schedules"
		self.modified = False
		self.schedDir = os.path.join(os.getcwd(), "data", "schedules")

		self.schedule = None
		self.scheduleTrains = []
		self.extraTrains = []
		self.templateTrains = []
		self.availableTrains = []
		self.trainTemplates = {}
		self.availableTemplates = []
		self.fullTemplatedTrains = []
		self.trainInfo = None

		self.allTrains = sorted([t for t in alltrains])
		self.setArrays(None)

		self.setTitle()

		btnFont = wx.Font(wx.Font(10, wx.FONTFAMILY_ROMAN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, faceName="Arial"))
		textFont = wx.Font(wx.Font(12, wx.FONTFAMILY_ROMAN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, faceName="Arial"))
		
		self.lbAll = wx.ListBox(self, wx.ID_ANY, choices=self.availableTrains, size=wx.Size(120, 330))
		self.lbAll.SetFont(textFont)
		self.Bind(wx.EVT_LISTBOX, self.onLbAllSelect, self.lbAll)
		
		self.lbSchedule = wx.ListBox(self, wx.ID_ANY, choices=self.scheduleTrains, size=wx.Size(120, 150))
		self.lbSchedule.SetFont(textFont)
		self.Bind(wx.EVT_LISTBOX, self.onLbScheduleSelect, self.lbSchedule)
			
		self.lbExtra = wx.ListBox(self, wx.ID_ANY, choices=self.extraTrains, size=wx.Size(120, 150))
		self.lbExtra.SetFont(textFont)
		self.Bind(wx.EVT_LISTBOX, self.onLbExtraSelect, self.lbExtra)
		
		self.bRightSch = wx.Button(self, wx.ID_ANY, ">>>")
		self.bRightSch.SetFont(btnFont)
		self.bRightSch.SetToolTip("Move the selected train to the right, from the all/available list to the scheduled list")
		self.Bind(wx.EVT_BUTTON, self.bRightSchPressed, self.bRightSch)
		
		self.bLeftSch = wx.Button(self, wx.ID_ANY, "<<<")
		self.bLeftSch.SetFont(btnFont)
		self.bLeftSch.SetToolTip("Move the selected train to the left, from the scheduled list to the all/available list")
		self.Bind(wx.EVT_BUTTON, self.bLeftSchPressed, self.bLeftSch)
		
		self.bRightExt = wx.Button(self, wx.ID_ANY, ">>>")
		self.bRightExt.SetFont(btnFont)
		self.bRightExt.SetToolTip("Move the selected train to the right, from the all/available list to the extra list")
		self.Bind(wx.EVT_BUTTON, self.bRightExtPressed, self.bRightExt)
		
		self.bLeftExt = wx.Button(self, wx.ID_ANY, "<<<")
		self.bLeftExt.SetFont(btnFont)
		self.bLeftExt.SetToolTip("Move the selected train to the left, from the extra list to the all/available list")
		self.Bind(wx.EVT_BUTTON, self.bLeftExtPressed, self.bLeftExt)
		
		self.bUp = wx.Button(self, wx.ID_ANY, "Up")
		self.bUp.SetFont(btnFont)
		self.bUp.SetToolTip("Move the selected train up to be earlier in the schedule")
		self.Bind(wx.EVT_BUTTON, self.bUpPressed, self.bUp)
		
		self.bDown = wx.Button(self, wx.ID_ANY, "Down")
		self.bDown.SetFont(btnFont)
		self.bDown.SetToolTip("Move the selected train down to be later in the schedule")
		self.Bind(wx.EVT_BUTTON, self.bDownPressed, self.bDown)
		
		hsizer = wx.BoxSizer(wx.HORIZONTAL)
		hsizer.AddSpacer(20)
		
		vsz = wx.BoxSizer(wx.VERTICAL)
		st = wx.StaticText(self, wx.ID_ANY, "Available:")
		st.SetFont(textFont)
		vsz.Add(st)
		vsz.AddSpacer(5)
		vsz.Add(self.lbAll)
		vsz.AddSpacer(10)
		hsizer.Add(vsz)
		
		hsizer.AddSpacer(10)
		
		vsz = wx.BoxSizer(wx.VERTICAL)
		vsz.AddSpacer(60)
		vsz.Add(self.bRightSch)
		vsz.AddSpacer(20)
		vsz.Add(self.bLeftSch)
		vsz.AddSpacer(110)
		vsz.Add(self.bRightExt)
		vsz.AddSpacer(20)
		vsz.Add(self.bLeftExt)
		hsizer.Add(vsz)
		
		hsizer.AddSpacer(10)
		
		vsz = wx.BoxSizer(wx.VERTICAL)
		st = wx.StaticText(self, wx.ID_ANY, "Scheduled:")
		st.SetFont(textFont)
		vsz.Add(st)
		vsz.AddSpacer(5)
		vsz.Add(self.lbSchedule)
		
		vsz.AddSpacer(5)
		st = wx.StaticText(self, wx.ID_ANY, "Extra:")
		st.SetFont(textFont)
		vsz.Add(st)
		vsz.AddSpacer(5)
		vsz.Add(self.lbExtra)
		vsz.AddSpacer(10)
		
		hsizer.Add(vsz)
		hsizer.AddSpacer(10)
		
		vsz = wx.BoxSizer(wx.VERTICAL)
		vsz.AddSpacer(60)
		vsz.Add(self.bUp)
		vsz.AddSpacer(20)
		vsz.Add(self.bDown)
		hsizer.Add(vsz)
		
		hsizer.AddSpacer(20)
		
		btnSizer = wx.BoxSizer(wx.HORIZONTAL)

		self.bLiveData = wx.Button(self, wx.ID_ANY, "Live Data\nSource", size=BTNSZ)
		self.bLiveData.SetFont(btnFont)
		self.bLiveData.SetToolTip("Load live train data")
		self.Bind(wx.EVT_BUTTON, self.bLiveDataPressed, self.bLiveData)
		btnSizer.Add(self.bLiveData)

		btnSizer.AddSpacer(10)

		self.bLoad = wx.Button(self, wx.ID_ANY, "Load\nSchedule", size=BTNSZ)
		self.bLoad.SetFont(btnFont)
		self.bLoad.SetToolTip("Load a train schedule from a file")
		self.Bind(wx.EVT_BUTTON, self.bLoadPressed, self.bLoad)
		btnSizer.Add(self.bLoad)

		btnSizer.AddSpacer(10)

		self.bSave = wx.Button(self, wx.ID_ANY, "Save\nSchedule", size=BTNSZ)
		self.bSave.SetFont(btnFont)
		self.bSave.SetToolTip("Save train schedule to a file")
		self.Bind(wx.EVT_BUTTON, self.bSavePressed, self.bSave)
		btnSizer.Add(self.bSave)

		btnSizer2 = wx.BoxSizer(wx.HORIZONTAL)

		self.bCards = wx.Button(self, wx.ID_ANY, "Print\nTrain Cards", size=BTNSZ)
		self.bCards.SetFont(btnFont)
		self.bCards.SetToolTip("Print Train Cards")
		self.Bind(wx.EVT_BUTTON, self.bCardsPressed, self.bCards)
		self.bCards.Enable(False)
		btnSizer2.Add(self.bCards)

		btnSizer2.AddSpacer(10)

		self.bSched = wx.Button(self, wx.ID_ANY, "Print\nSchedule", size=BTNSZ)
		self.bSched.SetFont(btnFont)
		self.bSched.SetToolTip("Print Train Schedule")
		self.Bind(wx.EVT_BUTTON, self.bSchedPressed, self.bSched)
		self.bSched.Enable(False)
		btnSizer2.Add(self.bSched)

		btnSizer3 = wx.BoxSizer(wx.HORIZONTAL)
		
		self.bOK = wx.Button(self, wx.ID_ANY, "OK", size=BTNSZ)
		self.bOK.SetFont(btnFont)
		self.bOK.SetToolTip("Exit the dialog box")
		self.Bind(wx.EVT_BUTTON, self.bOKPressed, self.bOK)
		btnSizer3.Add(self.bOK)
		
		btnSizer3.AddSpacer(10)
		
		self.bCancel = wx.Button(self, wx.ID_ANY, "Exit", size=BTNSZ)
		self.bCancel.SetFont(btnFont)
		self.bCancel.SetToolTip("Exit the dialog box discarding any trains chosen")
		self.Bind(wx.EVT_BUTTON, self.bCancelPressed, self.bCancel)
		btnSizer3.Add(self.bCancel)

		vsizer = wx.BoxSizer(wx.VERTICAL)		
		vsizer.AddSpacer(20)
		vsizer.Add(hsizer, 0, wx.ALIGN_CENTER_HORIZONTAL)
		vsizer.AddSpacer(20)
		vsizer.Add(btnSizer, 0, wx.ALIGN_CENTER_HORIZONTAL)
		vsizer.AddSpacer(20)
		vsizer.Add(btnSizer2, 0, wx.ALIGN_CENTER_HORIZONTAL)
		vsizer.AddSpacer(20)
		vsizer.Add(btnSizer3, 0, wx.ALIGN_CENTER_HORIZONTAL)
		vsizer.AddSpacer(20)
		
		self.SetSizer(vsizer)
		self.Layout()
		self.Fit()
		
		self.setButtons()

	def setModified(self, flag=True):
		if self.modified == flag:
			return

		self.modified = flag
		self.setTitle()
		
	def setTitle(self):
		tstr = self.titleString
		if self.modified:
			tstr += " *"

		self.SetTitle(tstr)
		
	def onLbAllSelect(self, _):
		self.setButtons()
		
	def setButtons(self):
		ix = self.lbAll.GetSelection()
		if ix == wx.NOT_FOUND:
			self.bRightSch.Enable(False)
			self.bRightExt.Enable(False)
		else:
			self.bRightSch.Enable(True)
			self.bRightExt.Enable(True)
			
		ix = self.lbSchedule.GetSelection()
		if ix == wx.NOT_FOUND:
			self.bUp.Enable(False)
			self.bDown.Enable(False)
			self.bLeftSch.Enable(False)
		else:
			self.bUp.Enable(ix != 0)
			self.bDown.Enable(ix != len(self.scheduleTrains)-1)
			self.bLeftSch.Enable(True)
		
		ix = self.lbExtra.GetSelection()
		if ix == wx.NOT_FOUND:
			self.bLeftExt.Enable(False)
		else:
			self.bLeftExt.Enable(True)

		schCount = self.lbSchedule.GetCount()
		extCount = self.lbExtra.GetCount()

		ena = schCount + extCount != 0
		self.bSched.Enable(ena)
		self.bCards.Enable(ena)
		
	def onLbScheduleSelect(self, _):
		self.setButtons()
		
	def onLbExtraSelect(self, _):
		self.setButtons()
		
	def bUpPressed(self, _):
		ix = self.lbSchedule.GetSelection()
		if ix == wx.NOT_FOUND or ix == 0:
			return
		
		s = self.scheduleTrains[ix]
		self.scheduleTrains[ix] = self.scheduleTrains[ix-1]
		self.scheduleTrains[ix-1] = s
		
		self.lbSchedule.SetItems(self.scheduleTrains)
		self.lbSchedule.SetSelection(ix-1)
		
		self.setButtons()
		self.setModified()
		
	def bDownPressed(self, _):
		ix = self.lbSchedule.GetSelection()
		if ix == wx.NOT_FOUND or ix >= len(self.scheduleTrains)-1:
			return
		
		s = self.scheduleTrains[ix]
		self.scheduleTrains[ix] = self.scheduleTrains[ix+1]
		self.scheduleTrains[ix+1] = s
		
		self.lbSchedule.SetItems(self.scheduleTrains)
		self.lbSchedule.SetSelection(ix+1)
		
		self.setButtons()
		self.setModified()
		
	def bRightSchPressed(self, _):
		avx = self.lbAll.GetSelection()
		if avx == wx.NOT_FOUND:
			return
		
		tid = self.availableTrains[avx]
		self.scheduleTrains.append(tid)
		self.lbSchedule.SetItems(self.scheduleTrains)
		self.setAvailableTrains()
		if avx >= len(self.availableTrains):
			avx = len(self.availableTrains)-1
		if avx < 0:
			self.lbAll.SetSelection(wx.NOT_FOUND)
		else:
			self.lbAll.SetSelection(avx)

		self.bRightSch.Enable(False)
		ix = len(self.scheduleTrains)-1
		self.lbSchedule.EnsureVisible(ix)
		self.lbSchedule.SetSelection(ix)
		self.setButtons()
		self.setModified()

	def bLeftSchPressed(self, _):
		ix = self.lbSchedule.GetSelection()
		if ix == wx.NOT_FOUND:
			return

		tid = self.scheduleTrains[ix]		
		del(self.scheduleTrains[ix])
		self.lbSchedule.SetItems(self.scheduleTrains)
		if ix >= len(self.scheduleTrains):
			ix = len(self.scheduleTrains)-1
		if ix < 0:
			self.lbSchedule.SetSelection(wx.NOT_FOUND)
		else:
			self.lbSchedule.SetSelection(ix)
		self.setAvailableTrains()
		try:
			ix = self.availableTrains.index(tid)
		except:
			ix = None
			
		self.bLeftSch.Enable(False)
		if ix is not None:
			self.lbAll.EnsureVisible(ix)
			self.lbAll.SetSelection(ix)
		self.setButtons()
		self.setModified()
	
	def bRightExtPressed(self, _):
		avx = self.lbAll.GetSelection()
		if avx == wx.NOT_FOUND:
			return
		
		tid = self.availableTrains[avx]
		self.extraTrains = sorted(self.extraTrains + [tid])
		ix = self.extraTrains.index(tid)
		self.lbExtra.SetItems(self.extraTrains)
		self.setAvailableTrains()
		if avx >= len(self.availableTrains):
			avx = len(self.availableTrains)-1
		if avx < 0:
			self.lbAll.SetSelection(wx.NOT_FOUND)
		else:
			self.lbAll.SetSelection(avx)
		self.bRightExt.Enable(False)
		if ix is not None:
			self.lbExtra.EnsureVisible(ix)
			self.lbExtra.SetSelection(ix)
		self.setButtons()
		self.setModified()

	def bLeftExtPressed(self, _):
		ix = self.lbExtra.GetSelection()
		if ix == wx.NOT_FOUND:
			return
		
		tid = self.extraTrains[ix]		
		del(self.extraTrains[ix])
		self.lbExtra.SetItems(self.extraTrains)
		if ix >= len(self.extraTrains):
			ix = len(self.extraTrains)-1
		if ix < 0:
			self.lbExtra.SetSelection(wx.NOT_FOUND)
		else:
			self.lbExtra.SetSelection(ix)
		self.setAvailableTrains()
		ix = self.availableTrains.index(tid)
		self.bLeftExt.Enable(False)
		if ix is not None:
			self.lbAll.EnsureVisible(ix)
			self.lbAll.SetSelection(ix)
		self.setButtons()
		self.setModified()

	def bCardsPressed(self, _):
		sched = Schedule()
		sched.setNewSchedule(self.scheduleTrains)
		sched.setNewExtras(self.extraTrains)
		self.trainCardsReport(sched)

	def bSchedPressed(self, _):
		ix = self.lbSchedule.GetSelection()
		if ix == wx.NOT_FOUND:
			selTrain = None
		else:
			selTrain = self.lbSchedule.GetString(ix)

		sched = Schedule()
		sched.setNewSchedule(self.scheduleTrains)
		sched.setNewExtras(self.extraTrains)
		self.scheduleReport(sched, selTrain, self.trainInfo)

	def setArrays(self, schedule):
		if schedule is None:
			self.schedule = None
			self.scheduleTrains = []
			self.extraTrains = []

		else:
			self.schedule = schedule
			self.scheduleTrains = schedule.getSchedule()
			self.extraTrains = schedule.getExtras()
			nTrains = len(self.scheduleTrains) + len(self.extraTrains)
			self.bCards.Enable(nTrains > 0)
			self.bSched.Enable(nTrains > 0)

		try:
			self.lbSchedule.SetItems(self.scheduleTrains)
		except:
			pass
		try:
			self.lbExtra.SetItems(self.extraTrains)
		except:
			pass
		self.setAvailableTrains()

	def setAvailableTrains(self):
		self.availableTrains = [t for t in self.allTrains if t not in self.scheduleTrains and t not in self.extraTrains]
		avtmp = ["%s(%s)" % (trid, self.trainTemplates[trid]) for trid in self.templateTrains]
		self.availableTemplates = [t for t in avtmp if t not in self.scheduleTrains and t not in self.extraTrains]
		self.availableTrains.extend(self.availableTemplates)
		try:
			self.lbAll.SetItems(self.availableTrains)
		except:
			pass

	def getSchedFiles(self):
		schedList = self.RRServer.Get("schedlist", {})
		if len(schedList) == 0:
			dlg = wx.MessageDialog(self, "No Schedules exist", "File Not Found", wx.OK | wx.ICON_WARNING)
			dlg.ShowModal()
			dlg.Destroy()
			return []

		return [s[:-5] for s in schedList]  # strip off the .json suffix

	def bLiveDataPressed(self, _):
		dlg = LiveDataSourceDlg(self)
		rc = dlg.ShowModal()
		dlg.Destroy()

		if rc == wx.ID_FILE1:
			at = self.RRServer.Get("activetrains", {})
			self.trainInfo = {}
			self.trainTemplates = {}
			self.templateTrains = []
			self.fullTemplatedTrains = []
			for trid, tinfo in at.items():
				if "template" in tinfo and tinfo["template"] is not None:
					tmpl = tinfo["template"]
					tidkey = "%s(%s)" % (trid, tmpl)
					self.trainTemplates[trid] = tmpl
					self.templateTrains.append(trid)
					self.fullTemplatedTrains.append(tidkey)
				else:
					tidkey = trid
				trk = None
				if "blocks" in tinfo and len(tinfo["blocks"]) > 0:
					trk = tinfo["blocks"][0]
				self.trainInfo[tidkey] = {"loco": tinfo.get("loco", None), "track": trk}

			self.templateTrains = sorted(self.templateTrains)
			self.fullTemplatedTrains = sorted(self.fullTemplatedTrains)

		elif rc == wx.ID_FILE2:
			trinfo = self.LoadSnapshot()
			if trinfo is None:
				return

			self.ProcessSnapshot(trinfo)

		elif rc == wx.ID_FILE3:
			wildcard = "JSON (*.json)|*.json"
			dlg = wx.FileDialog(
				self, message="Choose snapshot file to use ...", defaultDir=os.getcwd(),
				defaultFile="", wildcard=wildcard, style=wx.FD_OPEN
			)
			rc = dlg.ShowModal()
			if rc == wx.ID_CANCEL:
				dlg.Destroy()
				return

			fn = dlg.GetPath()
			dlg.Destroy()

			with open(fn, "r") as jfp:
				jdata = json.load(jfp)

			self.ProcessSnapshot(jdata)

		else:
			logging.error("unknown rc from select live source: %d" % rc)
			return

		self.setArrays(self.schedule)

	def ProcessSnapshot(self, trinfo):
		self.trainInfo = {}
		self.trainTemplates = {}
		self.templateTrains = []
		self.fullTemplatedTrains = []
		for trid, tinfo in trinfo.items():
			if trid == "PRELOAD":
				continue

			if "template" in tinfo:
				tmpl = tinfo["template"]
				fullName = "%s(%s)" % (trid, tmpl)
				self.trainTemplates[trid] = tmpl
				self.templateTrains.append(trid)
				self.fullTemplatedTrains.append(fullName)
			else:
				fullName = trid

			print("snapshot - tinfo = %s" % str(tinfo))
			trk = None
			if "blocks" in tinfo and len(tinfo["blocks"]) > 0:
				trk = tinfo["blocks"][0]
			self.trainInfo[fullName] = {"loco": tinfo.get("loco", None), "track": trk}

		self.templateTrains = sorted(self.templateTrains)
		self.fullTemplatedTrains = sorted(self.fullTemplatedTrains)

	def bLoadPressed(self, _):
		if self.modified:
			msg = "Pending changes will be lost\nPress Yes to continue\nPress No to cancel"
			dlg = wx.MessageDialog(self, msg, "Do you wish to continue schedule loading?",
				wx.YES_NO | wx.NO_DEFAULT | wx.ICON_WARNING)
			rc = dlg.ShowModal()
			dlg.Destroy()
			if rc != wx.ID_YES:
				return

		dlg = ChooseScheduleDlg(self, self.getSchedFiles(), False)
		rc = dlg.ShowModal()
		if rc != wx.ID_OK:
			dlg.Destroy()
			return

		schedNm = dlg.GetValue()
		dlg.Destroy()

		sched = Schedule()
		if not sched.load(schedNm, self.RRServer):
			return

		#determine if schedule references trains than are not in available trains
		oTrains = sched.getSchedule()
		tl = self.allTrains + self.fullTemplatedTrains
		oMissing = [t for t in oTrains if t not in tl]
		eTrains = sched.getExtras()
		eMissing = [t for t in eTrains if t not in tl]

		if len(oMissing) > 0 or len(eMissing) > 0:
			txt = "This schedule file references the following\ntrains that are not in the current roster:\n"
			if len(oMissing) > 0:
				txt += ("Scheduled: %s\n" % ",".join(oMissing))
			if len(eMissing) > 0:
				txt += ("Extra: %s\n" % ",".join(eMissing))
			txt += "\nPress\"Yes\" remove these trains from the schedule, or\n\"No\" to cancel."

			dlg = wx.MessageDialog(self, txt, "Referencing unknown trains",	wx.YES_NO | wx.ICON_WARNING)
			rc = dlg.ShowModal()
			dlg.Destroy()
			if rc != wx.ID_YES:
				return

			oNew = [t for t in oTrains if t in tl]
			eNew = [t for t in eTrains if t in tl]

			sched.setNewSchedule(oNew)
			sched.setNewExtras(eNew)

		self.setArrays(sched)
		self.setModified(False)
		self.setTitle()

	def bSavePressed(self, _):
		schList = self.getSchedFiles()
		dlg = ChooseScheduleDlg(self, schList, True)
		rc = dlg.ShowModal()
		if rc != wx.ID_OK:
			dlg.Destroy()
			return

		schedNm = dlg.GetValue()
		if schedNm in schList:
			msg = "Schedule %s already exists\nPress \"Yes\" to continue\nPress \"No\" to cancel" % schedNm
			dlg = wx.MessageDialog(self, msg, "Do you wish to over-write?",	wx.YES_NO | wx.NO_DEFAULT | wx.ICON_WARNING)
			rc = dlg.ShowModal()
			dlg.Destroy()
			if rc != wx.ID_YES:
				return

		sched = Schedule()
		sched.setNewSchedule(self.scheduleTrains)
		sched.setNewExtras(self.extraTrains)
		sched.save(schedNm, self.RRServer)

		msg = "Schedule %s has been saved with\n%d scheduled trains and\n%d extra trains" % (schedNm, len(self.scheduleTrains), len(self.extraTrains))
		dlg = wx.MessageDialog(self, msg, "Schedule saved", wx.OK | wx.ICON_INFORMATION)
		rc = dlg.ShowModal()
		dlg.Destroy()
		self.setModified(False)

	def LoadSnapshot(self):
		snapList = self.RRServer.Get("snaplist", {})
		if len(snapList) == 0:
			dlg = wx.MessageDialog(self, "No Snapshots exist", "File Not Found", wx.OK | wx.ICON_WARNING)
			dlg.ShowModal()
			dlg.Destroy()

		dlg = ChooseSnapshotDlg(self, snapList)
		rc = dlg.ShowModal()
		snapFile = dlg.GetResults()
		dlg.Destroy()
		if rc != wx.ID_OK:
			return None

		trjson = self.RRServer.Get("retrievesnapshot", {"file": snapFile})
		if trjson is None:
			dlg = wx.MessageDialog(self, "Snapshot %s does not exist" % snapFile, "File Not Found", wx.OK | wx.ICON_WARNING)
			dlg.ShowModal()
			dlg.Destroy()
			return None

		return trjson

	def bOKPressed(self, _):
		self.EndModal(wx.ID_OK)

	def bCancelPressed(self, _):
		self.doCancel()
		
	def onClose(self, _):
		self.doCancel()
		
	def doCancel(self):
		if self.modified:
			msg = "Pending changes will be lost\nPress Yes to continue\nPress No to cancel"
			dlg = wx.MessageDialog(self, msg, "Do you wish to exit dialog?",	wx.YES_NO | wx.NO_DEFAULT | wx.ICON_WARNING)
			rc = dlg.ShowModal()
			dlg.Destroy()
			if rc != wx.ID_YES:
				return

		self.EndModal(wx.ID_CANCEL)
		
	def getResults(self):
		results = Schedule()
		results.setNewSchedule(self.scheduleTrains)
		results.setNewExtras(self.extraTrains)
		
		return results


class ChooseScheduleDlg(wx.Dialog):
	def __init__(self, parent, schedules, allowentry):
		wx.Dialog.__init__(self, parent, wx.ID_ANY, "")
		self.Bind(wx.EVT_CLOSE, self.OnCancel)
		if allowentry:
			self.SetTitle("Choose/Enter schedule name")
		else:
			self.SetTitle("Choose schedule name")

		vszr = wx.BoxSizer(wx.VERTICAL)
		vszr.AddSpacer(20)

		if allowentry:
			style = wx.CB_DROPDOWN
		else:
			style = wx.CB_DROPDOWN | wx.CB_READONLY

		cb = wx.ComboBox(self, 500, "", size=wx.Size(160, -1), choices=schedules, style=style)
		self.cbSchedule = cb
		vszr.Add(cb, 0, wx.ALIGN_CENTER_HORIZONTAL)
		if not allowentry and len(schedules) > 0:
			self.cbSchedule.SetSelection(0)
		else:
			self.cbSchedule.SetSelection(wx.NOT_FOUND)

		vszr.AddSpacer(20)

		btnszr = wx.BoxSizer(wx.HORIZONTAL)

		bOK = wx.Button(self, wx.ID_ANY, "OK")
		self.Bind(wx.EVT_BUTTON, self.OnBOK, bOK)

		bCancel = wx.Button(self, wx.ID_ANY, "Cancel")
		self.Bind(wx.EVT_BUTTON, self.OnCancel, bCancel)

		btnszr.Add(bOK)
		btnszr.AddSpacer(20)
		btnszr.Add(bCancel)

		vszr.Add(btnszr, 0, wx.ALIGN_CENTER_HORIZONTAL)

		vszr.AddSpacer(20)

		hszr = wx.BoxSizer(wx.HORIZONTAL)
		hszr.AddSpacer(20)
		hszr.Add(vszr)

		hszr.AddSpacer(20)

		self.SetSizer(hszr)
		self.Layout()
		self.Fit()

	def GetValue(self):
		return self.cbSchedule.GetValue()

	def OnCancel(self, _):
		self.EndModal(wx.ID_CANCEL)

	def OnBOK(self, _):
		self.EndModal(wx.ID_OK)


class LiveDataSourceDlg(wx.Dialog):
	def __init__(self, parent):
		wx.Dialog.__init__(self, parent, wx.ID_ANY, "Choose Live Data Source")

		btnFont = wx.Font(wx.Font(10, wx.FONTFAMILY_ROMAN, wx.NORMAL, wx.BOLD, faceName="Arial"))

		hsizer = wx.BoxSizer(wx.HORIZONTAL)
		hsizer.AddSpacer(20)

		vsz = wx.BoxSizer(wx.VERTICAL)
		vsz.AddSpacer(20)

		self.bLayout = wx.Button(self, wx.ID_ANY, "Layout Data", size=BTNSZ)
		self.bLayout.SetFont(btnFont)
		self.bLayout.SetToolTip(
			"Use the train data from the currently active session")
		self.Bind(wx.EVT_BUTTON, self.OnBLayout, self.bLayout)
		vsz.Add(self.bLayout)
		vsz.AddSpacer(10)

		self.bSnapshot = wx.Button(self, wx.ID_ANY, "Stored Snapshot", size=BTNSZ)
		self.bSnapshot.SetFont(btnFont)
		self.bSnapshot.SetToolTip(
			"Use the train data from a stored snapshot")
		self.Bind(wx.EVT_BUTTON, self.OnBSnapshot, self.bSnapshot)
		vsz.Add(self.bSnapshot)
		vsz.AddSpacer(10)

		self.bLocal = wx.Button(self, wx.ID_ANY, "Local Snapshot", size=BTNSZ)
		self.bLocal.SetFont(btnFont)
		self.bLocal.SetToolTip(
			"Use the train data from a local snapshot")
		self.Bind(wx.EVT_BUTTON, self.OnBLocal, self.bLocal)
		vsz.Add(self.bLocal)

		vsz.AddSpacer(20)
		hsizer.Add(vsz)

		hsizer.AddSpacer(20)

		self.SetSizer(hsizer)
		self.Layout()
		self.Fit()

	def OnBLayout(self, _):
		self.EndModal(wx.ID_FILE1)

	def OnBSnapshot(self, _):
		self.EndModal(wx.ID_FILE2)

	def OnBLocal(self, _):
		self.EndModal(wx.ID_FILE3)
