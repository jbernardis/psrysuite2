import wx
import os
import json

from traineditor.trainsequences.traindlg import TrainDlg
from traineditor.trainsequences.train import Trains
from traineditor.trainsequences.blocksequence import BlockSequenceListCtrl
from traineditor.layoutdata import LayoutData

SIMSCRIPTFN = "simscripts.json"
ARSCRIPTFN =  "arscripts.json"

BRANCHENDS = ["F10", "R10"]

def StoppingSection(blk):
	return blk.endswith(".W") or blk.endswith(".E")
		

class TrainBlockSequencesDlg(wx.Dialog):
	def __init__(self, parent, rrserver):
		wx.Frame.__init__(self, parent, style=wx.DEFAULT_FRAME_STYLE)
		self.title = "PSRY Train Block Sequence Editor"
		self.Bind(wx.EVT_CLOSE, self.OnClose)
		self.RRServer = rrserver

		self.selectedTrain = None
		self.selectedRoute = None
		self.modified = False

		self.cbTrain = wx.ComboBox(self, wx.ID_ANY, "", size=(100, -1),
			 choices=[],
			 style=wx.CB_DROPDOWN | wx.TE_PROCESS_ENTER) #  | wx.CB_SORT)
		self.Bind(wx.EVT_COMBOBOX, self.OnCbTrain, self.cbTrain)
		self.Bind(wx.EVT_TEXT_ENTER, self.OnCbTrainTextEnter, self.cbTrain)
				
		self.chbEast = wx.CheckBox(self, wx.ID_ANY, "EastBound: ")
		self.chbEast.SetValue(True)
		self.Bind(wx.EVT_CHECKBOX, self.OnChbEastbound, self.chbEast)

		self.teStartBlock = wx.TextCtrl(self, wx.ID_ANY, "", size=(80, -1), style=wx.TE_READONLY)	
		self.teStartBlockTime = wx.TextCtrl(self, wx.ID_ANY, "", size=(80, -1), style=wx.TE_READONLY)	
		
		self.blockSeq = BlockSequenceListCtrl(self, height=200, readonly=True)
		
		
		self.bEditSteps = wx.Button(self, wx.ID_ANY, "Edit\nRoute", size=(80, 50))
		self.Bind(wx.EVT_BUTTON, self.OnBEditSteps, self.bEditSteps)
		self.bDelTrain = wx.Button(self, wx.ID_ANY, "Delete\nTrain", size=(80, 50))
		self.Bind(wx.EVT_BUTTON, self.OnBDelTrain, self.bDelTrain)
		
		trsz = wx.BoxSizer(wx.HORIZONTAL)
		trsz.Add(wx.StaticText(self, wx.ID_ANY, "Train: "), 0, wx.TOP, 5)
		trsz.AddSpacer(5)
		trsz.Add(self.cbTrain)
		
		self.bValCurrent = wx.Button(self, wx.ID_ANY, "Validate\nCurrent", size=(80, 50))
		self.Bind(wx.EVT_BUTTON, self.OnBValCurrent, self.bValCurrent)
		self.bValAll = wx.Button(self, wx.ID_ANY, "Validate\nAll", size=(80, 50))
		self.Bind(wx.EVT_BUTTON, self.OnBValAll, self.bValAll)
		self.bSave = wx.Button(self, wx.ID_ANY, "Save", size=(80, 50))
		self.Bind(wx.EVT_BUTTON, self.OnBSave, self.bSave)
		self.bExit = wx.Button(self, wx.ID_ANY, "Exit", size=(80, 50))
		self.Bind(wx.EVT_BUTTON, self.OnBExit, self.bExit)
		self.bRevert = wx.Button(self, wx.ID_ANY, "Revert", size=(80, 50))
		self.Bind(wx.EVT_BUTTON, self.OnBRevert, self.bRevert)

		self.cbUseRoute = wx.CheckBox(self, wx.ID_ANY, "Use route of train:")
		self.Bind(wx.EVT_CHECKBOX, self.OnChbUseRoute, self.cbUseRoute)
		self.chRoute = wx.Choice(self, wx.ID_ANY, choices=[])
		self.Bind(wx.EVT_CHOICE, self.OnChRoute, self.chRoute)

		routesz = wx.BoxSizer(wx.HORIZONTAL)
		routesz.Add(self.cbUseRoute)
		routesz.AddSpacer(5)
		routesz.Add(self.chRoute)

		buttonsz = wx.BoxSizer(wx.HORIZONTAL)

		buttonsz.AddSpacer(10)
		buttonsz.Add(self.bValCurrent)
		buttonsz.AddSpacer(20)
		buttonsz.Add(self.bValAll)
		buttonsz.AddSpacer(50)
		buttonsz.Add(self.bSave)
		buttonsz.AddSpacer(20)
		buttonsz.Add(self.bRevert)
		buttonsz.AddSpacer(50)
		buttonsz.Add(self.bExit)
		buttonsz.AddSpacer(10)
		
		vszl = wx.BoxSizer(wx.VERTICAL)
		vszl.AddSpacer(20)
		vszl.Add(trsz, 0, wx.ALIGN_CENTER_HORIZONTAL)
		vszl.AddSpacer(20)
		vszl.Add(self.chbEast, 0, wx.ALIGN_CENTER_HORIZONTAL)
		vszl.AddSpacer(20)
		
		vszr = wx.BoxSizer(wx.VERTICAL)
		vszr.AddSpacer(10)
		hsz = wx.BoxSizer(wx.HORIZONTAL)
		hsz.Add(wx.StaticText(self, wx.ID_ANY, "Starting Block: "))
		hsz.AddSpacer(5)
		hsz.Add(self.teStartBlock)
		hsz.AddSpacer(10)
		hsz.Add(wx.StaticText(self, wx.ID_ANY, "Time: "))
		hsz.AddSpacer(5)
		hsz.Add(self.teStartBlockTime)
		vszr.Add(hsz, 0, wx.ALIGN_CENTER_HORIZONTAL)
		vszr.AddSpacer(10)
		vszr.Add(self.blockSeq)
		vszr.AddSpacer(20)
		
		hsz = wx.BoxSizer(wx.HORIZONTAL)
		hsz.Add(self.bEditSteps)
		hsz.AddSpacer(20)
		hsz.Add(self.bDelTrain)
		vszr.Add(hsz, 0, wx.ALIGN_CENTER_HORIZONTAL)
		
		vszr.AddSpacer(20)
		
		hsz = wx.BoxSizer(wx.HORIZONTAL)
		hsz.AddSpacer(20)
		hsz.Add(vszl)
		hsz.AddSpacer(20)
		hsz.Add(vszr)
		hsz.AddSpacer(20)
		
		vsz = wx.BoxSizer(wx.VERTICAL)
		vsz.Add(hsz)
		vsz.AddSpacer(20)
		vsz.Add(routesz, 0, wx.ALIGN_CENTER_HORIZONTAL)
		vsz.AddSpacer(20)
		vsz.Add(buttonsz, 0, wx.ALIGN_CENTER_HORIZONTAL)
		vsz.AddSpacer(20)

		self.SetSizer(vsz)
		self.Fit()
		self.Layout()

		self.layout = LayoutData(self.RRServer)
		wx.CallAfter(self.Initialize)
		
	def Initialize(self):
		self.ShowTitle()
		self.bEditSteps.Enable(False)
		self.bValCurrent.Enable(False)

		self.loadTrains()
		self.SetRouteChoices(self.trains.GetTrainList())
		self.SetTrainChoices(self.trains.GetTrainList())

	def loadTrains(self):
		self.trains = Trains(self.RRServer)

	def SetTrainChoices(self, trlist=None):
		if trlist is not None:
			self.trainChoices = sorted([x for x in trlist])

		self.cbTrain.SetItems(self.trainChoices)
		if self.selectedTrain is not None:
			try:
				tx = self.trainChoices.index(self.selectedTrain)
			except ValueError:
				self.selectedTrain = None
				tx = 0

		if self.selectedTrain is None and len(self.trainChoices) > 0:
			tx = 0
			self.UpdateTrainSelection(self.trainChoices[0])
		elif self.selectedTrain is None:
			self.UpdateTrainSelection(None)

		if self.selectedTrain is not None:
			self.cbTrain.SetSelection(tx)
			tr = self.trains.GetTrainById(self.selectedTrain)
			self.selectedRoute = tr.GetRoute()
			if self.selectedRoute is None:
				self.cbUseRoute.SetValue(False)
				self.chRoute.SetSelection(wx.NOT_FOUND)
			else:
				self.cbUseRoute.SetValue(True)
				try:
					tx = self.routeChoices.index(self.selectedRoute)
				except ValueError:
					tx = wx.NOT_FOUND
				self.chRoute.SetSelection(tx)

			nsteps = tr.GetNSteps()
			self.cbUseRoute.Enable(nsteps == 0)
			self.chRoute.Enable(nsteps == 0)
		else:
			self.cbTrain.SetSelection(wx.NOT_FOUND)
			self.cbUseRoute.Enable(False)
			self.chRoute.Enable(False)

		self.bDelTrain.Enable(self.selectedTrain is not None)

	def SetRouteChoices(self, trlist=None):
		if trlist is not None:
			self.routeChoices = []
			for trid in trlist:
				tr = self.trains.GetTrainById(trid)
				if tr is None:
					continue

				if tr.GetNSteps() > 0:
					self.routeChoices.append(trid)
		else:
			self.routeChoices = []

		self.chRoute.SetItems(self.routeChoices)
		if self.selectedRoute is not None:
			try:
				tx = self.routeChoices.index(self.selectedRoute)
			except ValueError:
				self.selectedRoute = None
				tx = wx.NOT_FOUND

			self.chRoute.SetSelection(tx)
		else:
			self.chRoute.SetSelection(wx.NOT_FOUND)

	def AddTrainChoice(self, newtid):
		if newtid in self.trainChoices:
			return False
		
		dlg = wx.MessageDialog(self, "Train %s does not yet exist.\nDo you wish to add it?" % newtid, 'Train does not exist', wx.YES_NO | wx.NO_DEFAULT | wx.ICON_INFORMATION)
		rc = dlg.ShowModal()
		dlg.Destroy()
		
		if rc != wx.ID_YES:
			self.SetTrainChoices()
			return False
		
		self.trainChoices.append(newtid)
		self.selectedTrain = newtid
		self.trainChoices = sorted(self.trainChoices)
		self.trains.AddTrain(newtid, self.chbEast.IsChecked())
		self.SetTrainChoices()
		
		self.SetModified()
		
		return True

	def ShowTitle(self):
		titleString = self.title
		if self.modified:
			titleString += " *"
		self.SetTitle(titleString)
		
	def OnCbTrain(self, evt):
		tx = self.cbTrain.GetSelection()
		if tx is None or tx == wx.NOT_FOUND:
			tid = None
		else:
			tid = self.cbTrain.GetString(tx)

		self.UpdateTrainSelection(tid)

	def OnChbUseRoute(self, evt):
		flag = self.cbUseRoute.GetValue()
		if flag:
			try:
				rt = self.routeChoices[0]
			except (KeyError, IndexError):
				rt = None

			self.chRoute.SetSelection(wx.NOT_FOUND if rt is None else 0)
			tr = self.trains.GetTrainById(self.selectedTrain)
			tr.SetRoute(rt)
			self.SetModified()
			self.bEditSteps.Enable(False)

		else:
			tr = self.trains.GetTrainById(self.selectedTrain)
			otid = tr.GetRoute()
			tr.SetRoute(None)
			self.SetModified(otid is not None)
			self.chRoute.SetSelection(wx.NOT_FOUND)
			self.bEditSteps.Enable(True)

	def OnChRoute(self, evt):
		tx = self.chRoute.GetSelection()
		if tx is None or tx == wx.NOT_FOUND:
			tid = None
		else:
			tid = self.chRoute.GetString(tx)

		tr = self.trains.GetTrainById(self.selectedTrain)
		otid = tr.GetRoute()
		if otid != tid:
			tr.SetRoute(tid)
			self.SetModified()
			self.SetModified()

	def OnCbTrainTextEnter(self, evt):
		tid = evt.GetString()
		self.UpdateTrainSelection(tid)
		
	def UpdateTrainSelection(self, tid):
		if tid is None:
			self.bEditSteps.Enable(False)
			self.bValCurrent.Enable(False)
			self.currentTrain = None
			self.blockSeq.SetItems([])
			return
		if tid not in self.trainChoices:
			if not self.AddTrainChoice(tid):
				if self.currentTrain is None:
					self.bEditSteps.Enable(False)
					self.bValCurrent.Enable(False)
					self.currentTrain = None
					self.blockSeq.SetItems([])
					return

				self.selectedTrain = self.currentTrain.GetTrainID()
			else:
				self.selectedTrain = tid
		else:
			self.selectedTrain = tid

		tr = self.trains.GetTrainById(self.selectedTrain)
		self.currentTrain = tr
		if self.currentTrain.GetNSteps() > 0:  # train with steps defined
			self.chbEast.SetValue(tr.IsEast())
			self.blockSeq.SetItems(self.currentTrain.GetSteps())
			self.startBlock = self.currentTrain.GetStartBlock()
			self.startSubBlock = self.currentTrain.GetStartSubBlock()
			self.startBlockTime = self.currentTrain.GetStartBlockTime()
			self.ShowStartBlock()
			self.cbUseRoute.Enable(False)
			self.cbUseRoute.SetValue(False)
			self.chRoute.SetSelection(wx.NOT_FOUND)
			self.chRoute.Enable(False)
			self.bEditSteps.Enable(True)

		elif tr.GetRoute() is not None:  # train that is based on another train
			print("route for train %s is %s" % (self.selectedTrain, tr.GetRoute()))
			self.selectedRoute = tr.GetRoute()
			self.blockSeq.SetItems([])
			self.cbUseRoute.Enable(True)
			self.cbUseRoute.SetValue(True)
			try:
				tx = self.routeChoices.index(self.selectedRoute)
			except ValueError:
				tx = wx.NOT_FOUND
			self.chRoute.SetSelection(tx)
			self.chRoute.Enable(True)
			self.bEditSteps.Enable(False)

		else:  #  train that hasn't specified yet
			self.selectedRoute = None
			self.blockSeq.SetItems([])
			self.cbUseRoute.Enable(True)
			self.cbUseRoute.SetValue(False)
			self.chRoute.SetSelection(wx.NOT_FOUND)
			self.chRoute.Enable(True)
			self.bEditSteps.Enable(True)

	def ShowStartBlock(self):		
		if self.startBlock is not None:
			if self.startSubBlock is None:
				sbString = self.startBlock
			else:
				sbString = "%s(%s)" % (self.startBlock, self.startSubBlock)
				
			self.teStartBlock.SetValue(sbString)
		else:
			self.teStartBlock.SetValue("")
		if self.startBlockTime is None:
			self.teStartBlockTime.SetValue("")
		else:
			self.teStartBlockTime.SetValue("%d" % self.startBlockTime)

	def OnChbEastbound(self, evt):
		self.currentTrain.SetDirection(self.chbEast.IsChecked())
		self.SetModified()

	def OnBEditSteps(self, _):
		dlg = TrainDlg(self, self.currentTrain, self.layout)
		rc = dlg.ShowModal()
		if rc == wx.ID_OK:
			results = dlg.GetResults()
			
		dlg.Destroy()
		
		if rc != wx.ID_OK:
			return
		
		self.currentTrain.SetSteps(results["steps"])
		self.currentTrain.SetStartBlock(results["startblock"])
		self.currentTrain.SetStartSubBlock(results["startsubblock"])
		self.currentTrain.SetStartBlockTime(results["time"])
		self.blockSeq.SetItems(self.currentTrain.GetSteps())
		self.startBlock = self.currentTrain.GetStartBlock()
		self.startSubBlock = self.currentTrain.GetStartSubBlock()
		self.startBlockTime = self.currentTrain.GetStartBlockTime()
		self.ShowStartBlock()
		self.SetModified()

		l = len(results["steps"])
		if l > 0:
			self.currentTrain.SetRoute(None)
			self.cbUseRoute.SetValue(False)
			self.chRoute.SetSelection(wx.NOT_FOUND)
		self.chRoute.Enable(l == 0)
		self.cbUseRoute.Enable(l == 0)
		
	def validateSequence(self, blk, steps):
		badTransitions = []
		for step in steps:
			stepList = [step["block"], step["signal"], step["os"], step["route"]]
			if blk in BRANCHENDS and step["block"] in BRANCHENDS and blk != step["block"]:
				# opposite ends of the branch line are considered adjacent
				pass
			else:
				availableBlocks = []
				rteList = self.layout.GetRoutesForBlock(blk)
				for r in rteList:
					e = self.layout.GetRouteEnds(r)
					s = self.layout.GetRouteSignals(r)
					os = self.layout.GetRouteOS(r)
					if e[0] == blk:
						availableBlocks.append([e[1], s[0], os, r])
					elif e[1] == blk:
						availableBlocks.append([e[0], s[1], os, r])

				if stepList not in availableBlocks:
					badTransitions.append("Block %s  ==>  Block %s via signal %s OS %s Route %s" % (blk, stepList[0], stepList[1], stepList[2], stepList[3]))

			blk = step["block"] # move on to the next block
		
		return badTransitions
		
	def OnBDelTrain(self, _):
		if self.currentTrain is None:
			return
		
		tid = self.currentTrain.GetTrainID()
		dlg = wx.MessageDialog(self, "Are you sure you want to delete train %s?\nPress \"Yes\" to continue,\nor \"No\" to cancel." % tid,
				'Confirm train deletion', wx.YES_NO | wx.ICON_WARNING)
		rc = dlg.ShowModal()
		dlg.Destroy()
		if rc != wx.ID_YES:
			return

		self.trainChoices.remove(tid)
		self.trains.DelTrainByTID(tid)
		self.SetTrainChoices()
		
		self.SetModified()
		
	def SetModified(self, flag=True):
		self.modified = flag
		self.ShowTitle()

	def OnBValCurrent(self, _):
		steps = self.currentTrain.GetSteps()
		startBlock = self.currentTrain.GetStartBlock()
		
		badTransitions = self.validateSequence(startBlock, steps)
		title = "Validation Results for Train %s" % self.currentTrain.GetTrainID()		
		if len(badTransitions) == 0:
			dlg = wx.MessageDialog(self, 'Block sequence is correct!',
					title, wx.OK | wx.ICON_INFORMATION)
		else:
			msg = "The following block transitions are incorrect:\n " + "\n ".join(badTransitions)
			dlg = wx.MessageDialog(self, msg,
					title, wx.OK | wx.ICON_ERROR)
			
		dlg.ShowModal()
		dlg.Destroy()

	def OnBValAll(self, _):
		trainResults = {}
		for tr in self.trains:
			trid = tr.GetTrainID()
			steps = tr.GetSteps()
			startBlock = tr.GetStartBlock()
			trainResults[trid] = self.validateSequence(startBlock, steps)

		results = ""
		errors = 0			
		for trid in sorted(trainResults):
			t = trainResults[trid]
			errors += len(t)
			if len(t) == 0:
				results += "Train %s: Correct\n" % trid
			else:
				results += "Train %s:\n" % trid
				for r in t:
					results += "  %s\n" % r

		if errors == 0:
			results = "All trains are correct"
		else:
			results = "The following block transitions are incorrect:\n" + results

		dlg = wx.MessageDialog(self, results,
			"Validation Results for ALL Trains", wx.OK | (wx.ICON_ERROR if errors != 0 else wx.ICON_INFORMATION))
			
		dlg.ShowModal()
		dlg.Destroy()

	def OnBSave(self, _):
		self.trains.Save()
		self.SetModified(False)
		dlg = wx.MessageDialog(self, 'Train list has been saved', 'Data Saved', wx.OK | wx.ICON_INFORMATION)
		dlg.ShowModal()
		dlg.Destroy()

	def OnBExit(self, _):
		self.doExit()
		
	def OnBRevert(self, _):
		if self.modified:
			dlg = wx.MessageDialog(self, 'Train(s) have been modified.\nAre you sure you want to revert without saving?\nPress "Yes" to revert and lose changes,\nor "No" to return and save them.',
					'Changes will be lost', wx.YES_NO | wx.ICON_WARNING)
			rc = dlg.ShowModal()
			dlg.Destroy()
			if rc != wx.ID_YES:
				return
		
		self.Initialize()
		
	def OnClose(self, _):
		self.doExit()
		
	def doExit(self):
		if self.modified:
			dlg = wx.MessageDialog(self, 'Train(s) have been modified.\nAre you sure you want to exit without saving?\nPress "Yes" to exit and lose changes,\nor "No" to return and save them.',
					'Changes will be lost', wx.YES_NO | wx.ICON_WARNING)
			rc = dlg.ShowModal()
			dlg.Destroy()
			if rc != wx.ID_YES:
				return
		self.Destroy()
		
