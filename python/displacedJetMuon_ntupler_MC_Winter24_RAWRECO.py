import FWCore.ParameterSet.Config as cms
from FWCore.ParameterSet.VarParsing import VarParsing
#------ Setup ------#

#initialize the process
process = cms.Process("displacedJetMuonNtupler")
process.load("FWCore.MessageService.MessageLogger_cfi")
process.load("Configuration.EventContent.EventContent_cff")
process.load("cms_lpc_llp.llp_ntupler.metFilters_cff_2018")


options = VarParsing ('analysis')
# must match the GT of the RECO step that made the input
options.register('globalTag', '133X_mcRun3_2024_realistic_v8', VarParsing.multiplicity.singleton, VarParsing.varType.string, "global tag")
# DT digis + DT SimHits (signal and crossing-frame PU)
options.register('saveDTSimDigi', True, VarParsing.multiplicity.singleton, VarParsing.varType.bool, "save DT digis and SimHits")
options.register('cscSimHitBXMin', -999, VarParsing.multiplicity.singleton, VarParsing.varType.int, "lowest CSC SimHit BX to save")
options.register('cscSimHitBXMax', 999, VarParsing.multiplicity.singleton, VarParsing.varType.int, "highest CSC SimHit BX to save")
options.register('cscStripFiredOnly', True, VarParsing.multiplicity.singleton, VarParsing.varType.bool, "save only strips with max-min ADC > 13.3")

options.parseArguments()

 
readFiles = cms.untracked.vstring()
if len(options.inputFiles) == 1 and options.inputFiles[0].endswith(".txt"):
    with open(options.inputFiles[0]) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#"):
                readFiles.append(line)
else:
    readFiles.extend(options.inputFiles)


process.source = cms.Source("PoolSource",
    fileNames = readFiles
)

process.options = cms.untracked.PSet(

)

process.maxEvents = cms.untracked.PSet( input = cms.untracked.int32(-1) )
process.MessageLogger.cerr.FwkReport.reportEvery = 500

#TFileService for output
process.TFileService = cms.Service("TFileService",
	fileName = cms.string('ntupled.root'),
    closeFileFast = cms.untracked.bool(True)
)

#Omittig duplicate errors as events are duplicated in the local production! better remove this in future!!!
process.source.duplicateCheckMode = cms.untracked.string('noDuplicateCheck')


# print("duplicateCheckMode =", process.source.duplicateCheckMode.value())
# print("nFiles =", len(process.source.fileNames))
# print("firstFiles =", list(process.source.fileNames)[:3])

#load run conditions
process.load('Configuration.StandardSequences.FrontierConditions_GlobalTag_cff')
#process.load('Configuration.Geometry.GeometryIdeal_cff')
#process.load('Configuration.StandardSequences.MagneticField_38T_cff')
process.load('Configuration.StandardSequences.GeometryRecoDB_cff')
process.load('Configuration.StandardSequences.MagneticField_AutoFromDBCurrent_cff')

#------ Declare the correct global tag ------#

# process.GlobalTag.globaltag = '124X_dataRun3_Prompt_v4'
process.GlobalTag.globaltag = options.globalTag

#------ If we add any inputs beyond standard event content, import them here ------#
process.load('RecoMET.METFilters.BadPFMuonFilter_cfi')


process.output = cms.OutputModule("PoolOutputModule",
    compressionAlgorithm = cms.untracked.string('LZMA'),
    compressionLevel = cms.untracked.int32(4),
    dataset = cms.untracked.PSet(
        dataTier = cms.untracked.string(''),
        filterName = cms.untracked.string('')
    ),
    dropMetaData = cms.untracked.string('ALL'),
    eventAutoFlushCompressedSize = cms.untracked.int32(-900),
    fastCloning = cms.untracked.bool(False),
    fileName = cms.untracked.string('miniAOD-prod_PAT.root'),
    outputCommands = cms.untracked.vstring('keep *'),
)



 
#------ Analyzer ------#

# For AOD Track variables
process.load("RecoTracker.TkNavigation.NavigationSchoolESProducer_cfi")
process.MaterialPropagator = cms.ESProducer('PropagatorWithMaterialESProducer',
    ComponentName = cms.string('PropagatorWithMaterial'),
    Mass = cms.double(0.105),
    MaxDPhi = cms.double(1.6),
    PropagationDirection = cms.string('alongMomentum'),
    SimpleMagneticField = cms.string(''),
    ptMin = cms.double(-1.0),
    useRungeKutta = cms.bool(False)
)

process.TransientTrackBuilderESProducer = cms.ESProducer('TransientTrackBuilderESProducer',
    ComponentName = cms.string('TransientTrackBuilder')
)


#list input collections
process.ntuples = cms.EDAnalyzer('displacedJetMuon_ntupler',
    isData = cms.bool(False),
    useGen = cms.bool(True),
    isRECO = cms.bool(True),                                
    isRAW = cms.bool(False),                                
    isBParkAOD = cms.bool(False),
    isFastsim = cms.bool(False),
    readMuonDigis = cms.bool(True),
    enableTriggerInfo = cms.bool(True),
    enableEcalRechits = cms.bool(False),
    enableCaloJet = cms.bool(True),
    enableGenLLPInfo = cms.bool(True),
    readGenVertexTime = cms.bool(False),#need to be false for displaced samples
    genParticles_t0 = cms.InputTag("genParticles", "t0", ""),
    triggerPathNamesFile = cms.string("cms_lpc_llp/llp_ntupler/data/trigger_names_llp_Run2022_v1.dat"),
    eleHLTFilterNamesFile = cms.string("SUSYBSMAnalysis/RazorTuplizer/data/RazorElectronHLTFilterNames.dat"),
    muonHLTFilterNamesFile = cms.string("cms_lpc_llp/llp_ntupler/data/MuonHLTFilterNames.dat"),
    photonHLTFilterNamesFile = cms.string("SUSYBSMAnalysis/RazorTuplizer/data/RazorPhotonHLTFilterNames.dat"),

    #vertices = cms.InputTag("offlinePrimaryVerticesWithBS"),  # for non-timing case
    vertices = cms.InputTag("offlinePrimaryVertices", "", "RECO"),
    muons = cms.InputTag("muons"),
    electrons = cms.InputTag("gedGsfElectrons"),
    taus = cms.InputTag("selectedPatTaus"),
    photons = cms.InputTag("gedPhotons"),
    jetsCalo = cms.InputTag("ak4CaloJets","","RECO"),
    jetsPF = cms.InputTag("ak4PFJets"),
    #jets = cms.InputTag("ak4PFJetsCHS"),
    jets = cms.InputTag("selectedPatJets"),
    jetsPuppi = cms.InputTag("ak4PFJets"),
    #jetsAK8 = cms.InputTag("ak8PFJetsCHS"),
    jetsAK8 = cms.InputTag("selectedPatJetsAK8PFCHS"),

    #mets = cms.InputTag("slimmedMETs"),
    mets = cms.InputTag("patMETs"),
    #metsNoHF = cms.InputTag("pfMet30"),
    metsPuppi = cms.InputTag("pfMet"),
    pfCands = cms.InputTag("particleFlow","","RECO"),

    #packedPfCands = cms.InputTag("packedPFCandidates"),

    genParticles = cms.InputTag("genParticles"),
    MuonCSCSimHits = cms.InputTag("g4SimHits", "MuonCSCHits","SIM"),
    # classical-mixing SimHits with BX; used over MuonCSCSimHits when present
    MuonCSCSimHitsXF = cms.untracked.InputTag("mix", "g4SimHitsMuonCSCHits"),
    # drop CSC SimHits with energyLoss <= this [GeV]
    cscSimHitElossMin = cms.untracked.double(2e-6),
    # save CSC SimHits only in this BX window (mixing still simulates -12..+3); default = all
    cscSimHitBXMin = cms.untracked.int32(options.cscSimHitBXMin),
    cscSimHitBXMax = cms.untracked.int32(options.cscSimHitBXMax),
    cscStripFiredOnly = cms.untracked.bool(options.cscStripFiredOnly),
    # DT block; needs simMuonDTDigis and mix:g4SimHitsMuonDTHits kept in production
    saveDTSimDigi = cms.untracked.bool(options.saveDTSimDigi),
    MuonDTSimHits = cms.untracked.InputTag("g4SimHits", "MuonDTHits", "SIM"),
    MuonDTSimHitsXF = cms.untracked.InputTag("mix", "g4SimHitsMuonDTHits"),
    MuonDTDigi = cms.untracked.InputTag("simMuonDTDigis"),
    dtSimHitElossMin = cms.untracked.double(2e-6),
    MuonCSCComparatorDigi = cms.InputTag("simMuonCSCDigis", "MuonCSCComparatorDigi", "HLT"),
    MuonCSCStripDigi = cms.InputTag("simMuonCSCDigis", "MuonCSCStripDigi"),
    MuonCSCWireDigi = cms.InputTag("simMuonCSCDigis", "MuonCSCWireDigi"),
    MuonCSCWireDigiSimLinks = cms.InputTag( "simMuonCSCDigis", "MuonCSCWireDigiSimLinks", "HLT"),
    MuonCSCStripDigiSimLinks = cms.InputTag("simMuonCSCDigis","MuonCSCStripDigiSimLinks", "HLT"),

    #packedGenParticles = cms.InputTag("packedGenParticles"),
    #prunedGenParticles = cms.InputTag("prunedGenParticles"),
    genMetsCalo = cms.InputTag("genMetCalo"),
    genMetsTrue = cms.InputTag("genMetTrue"),
    genJets = cms.InputTag("ak4GenJets"),

    triggerBits = cms.InputTag("TriggerResults","","HLT"),
    #triggerBits = cms.InputTag("TriggerResults","","RECO"),
    hepMC = cms.InputTag("generatorSmeared", "", "SIM"),

    triggerPrescales = cms.InputTag("patTrigger"),
    triggerObjects = cms.InputTag("selectedPatTrigger"),

    metFilterBits = cms.InputTag("TriggerResults", "", "RECO"),

    #hbheNoiseFilter = cms.InputTag("HBHENoiseFilterResultProducer","HBHENoiseFilterResult"),
    #hbheTightNoiseFilter = cms.InputTag("HBHENoiseFilterResultProducer","HBHENoiseFilterResultRun2Tight"),
    #hbheIsoNoiseFilter = cms.InputTag("HBHENoiseFilterResultProducer","HBHEIsoNoiseFilterResult"),

    #BadChargedCandidateFilter = cms.InputTag("BadChargedCandidateFilter",""),
    #BadMuonFilter = cms.InputTag("BadPFMuonFilter",""),

    #lheInfo = cms.InputTag("externalLHEProducer", "", ""),
    genInfo = cms.InputTag("generator", "", "SIM"),

    tracks = cms.InputTag("generalTracks", "", "RECO"),
    #trackTime = cms.InputTag("trackTimeValueMapProducer","generalTracksConfigurableFlatResolutionModel"),
    #trackTimeReso = cms.InputTag("trackTimeValueMapProducer","generalTracksConfigurableFlatResolutionModelResolution"),

    # classical mixing: addPileupInfo, premixed: mixData
    puInfo = cms.InputTag("addPileupInfo", "", "HLT"),  # classical mixing (minbias/PU sample)
    # puInfo = cms.InputTag("mixData", "", "HLT"),      # premixed samples (ggH/DY)

    #hcalNoiseInfo = cms.InputTag("hcalnoise", "", "RECO"),

    #secondaryVertices = cms.InputTag("inclusiveSecondaryVertices", "", "RECO"),
    secondaryVertices = cms.InputTag("inclusiveCandidateSecondaryVertices","", "RECO"),

    rhoAll = cms.InputTag("fixedGridRhoAll", "", "RECO"),

    rhoFastjetAll = cms.InputTag("fixedGridRhoFastjetAll", "", "RECO"),
    rhoFastjetAllCalo = cms.InputTag("fixedGridRhoFastjetAllCalo", "", "RECO"),
    rhoFastjetCentralCalo = cms.InputTag("fixedGridRhoFastjetCentralCalo", "", "RECO"),
    rhoFastjetCentralChargedPileUp = cms.InputTag("fixedGridRhoFastjetCentralChargedPileUp", "", "RECO"),
    rhoFastjetCentralNeutral = cms.InputTag("fixedGridRhoFastjetCentralNeutral", "", "RECO"),

    beamSpot = cms.InputTag("offlineBeamSpot", "", "RECO"),
    pfClusters = cms.InputTag("particleFlowClusterECAL","","RECO"),
    ebRecHits = cms.InputTag("reducedEcalRecHitsEB", "","RECO"),
    #ebRecHits = cms.InputTag("EcalRecHit", "reducedEcalRecHitsEB", "RECO"),
    eeRecHits  = cms.InputTag("reducedEcalRecHitsEE", "","RECO"),
    esRecHits = cms.InputTag("reducedEcalRecHitsES", "","RECO"),
    #ebeeClusters = cms.InputTag("reducedEgamma", "reducedEBEEClusters", "RECO"),
    ebeeClusters = cms.InputTag("particleFlowEGamma", "EBEEClusters", "RECO"),
    esClusters = cms.InputTag("particleFlowEGamma", "ESClusters", "RECO"),
    #conversions = cms.InputTag("reducedEgamma", "reducedConversions", "RECO"),
    conversions = cms.InputTag("allConversions", "", "RECO"),

    #singleLegConversions = cms.InputTag("reducedEgamma", "reducedSingleLegConversions", "RECO"),
    singleLegConversions = cms.InputTag("particleFlowEGamma", "", "RECO"),

    gedGsfElectronCores = cms.InputTag("gedGsfElectronCores", "", "RECO"),
    gedPhotonCores = cms.InputTag("gedPhotonCore", "", "RECO"),
    generalTracks = cms.InputTag("generalTracks", "", "RECO"),
    #superClusters = cms.InputTag("reducedEgamma", "reducedSuperClusters", "RECO"),

    #lostTracks = cms.InputTag("lostTracks", "", "RECO")

    electron_cutbasedID_decisions_veto = cms.InputTag("egmGsfElectronIDs", "cutBasedElectronID-Fall17-94X-V2-veto", ""),
    electron_cutbasedID_decisions_loose = cms.InputTag("egmGsfElectronIDs", "cutBasedElectronID-Fall17-94X-V2-loose", ""),
    electron_cutbasedID_decisions_medium = cms.InputTag("egmGsfElectronIDs", "cutBasedElectronID-Fall17-94X-V2-medium", ""),
    electron_cutbasedID_decisions_tight = cms.InputTag("egmGsfElectronIDs", "cutBasedElectronID-Fall17-94X-V2-tight", ""),
    electron_mvaIsoID_decisions_wp80 = cms.InputTag("egmGsfElectronIDs", "mvaEleID-Fall17-iso-V2-wp80", ""),
    electron_mvaIsoID_decisions_wp90 = cms.InputTag("egmGsfElectronIDs", "mvaEleID-Fall17-iso-V2-wp90", ""),
    electron_mvaIsoID_decisions_wpHZZ = cms.InputTag("egmGsfElectronIDs", "mvaEleID-Fall17-iso-V2-wpHZZ", ""),
    electron_mvaIsoID_decisions_wpLoose = cms.InputTag("egmGsfElectronIDs", "mvaEleID-Fall17-iso-V2-wpLoose", ""),
    electron_mvaNoIsoID_decisions_wp80 = cms.InputTag("egmGsfElectronIDs", "mvaEleID-Fall17-noIso-V2-wp80", ""),
    electron_mvaNoIsoID_decisions_wp90 = cms.InputTag("egmGsfElectronIDs", "mvaEleID-Fall17-noIso-V2-wp90", ""),
    electron_mvaNoIsoID_decisions_wpLoose = cms.InputTag("egmGsfElectronIDs", "mvaEleID-Fall17-noIso-V2-wpLoose", ""),
    photon_cutbasedID_decisions_loose = cms.InputTag("egmPhotonIDs", "cutBasedPhotonID-Fall17-94X-V2-loose", ""),
    photon_cutbasedID_decisions_medium = cms.InputTag("egmPhotonIDs", "cutBasedPhotonID-Fall17-94X-V2-medium", ""),
    photon_cutbasedID_decisions_tight = cms.InputTag("egmPhotonIDs", "cutBasedPhotonID-Fall17-94X-V2-tight", ""),
    photon_mvaID_decisions_wp80 = cms.InputTag("egmPhotonIDs", "mvaPhoID-RunIIFall17-v2-wp80", ""),
    photon_mvaID_decisions_wp90 = cms.InputTag("egmPhotonIDs", "mvaPhoID-RunIIFall17-v2-wp90", ""),
)

#Add jettiness for AK8 jets
process.load('RecoJets.JetProducers.nJettinessAdder_cfi')
process.NjettinessAK8CHS = process.Njettiness.clone()


from PhysicsTools.SelectorUtils.tools.vid_id_tools import *
electron_id_config = cms.PSet(electron_ids = cms.vstring([                   
                    'RecoEgamma.ElectronIdentification.Identification.cutBasedElectronID_Summer16_80X_V1_cff',
                    'RecoEgamma.ElectronIdentification.Identification.mvaElectronID_Spring16_GeneralPurpose_V1_cff',
                    'RecoEgamma.ElectronIdentification.Identification.mvaElectronID_Spring16_HZZ_V1_cff',
                    'RecoEgamma.ElectronIdentification.Identification.cutBasedElectronID_Fall17_94X_V2_cff',
                    'RecoEgamma.ElectronIdentification.Identification.mvaElectronID_Fall17_noIso_V2_cff', 
                    'RecoEgamma.ElectronIdentification.Identification.mvaElectronID_Fall17_iso_V2_cff',
                    ]))  
photon_id_config = cms.PSet(photon_ids = cms.vstring([                   
            'RecoEgamma.PhotonIdentification.Identification.cutBasedPhotonID_Spring16_V2p2_cff',
            'RecoEgamma.PhotonIdentification.Identification.mvaPhotonID_Spring16_nonTrig_V1_cff',
            "RecoEgamma.PhotonIdentification.Identification.mvaPhotonID_Fall17_94X_V2_cff",
            "RecoEgamma.PhotonIdentification.Identification.cutBasedPhotonID_Fall17_94X_V2_cff"            
                    ]))  


                 
switchOnVIDElectronIdProducer(process,DataFormat.AOD)
switchOnVIDPhotonIdProducer(process,DataFormat.AOD) 
process.egmGsfElectronIDs.physicsObjectSrc = cms.InputTag("gedGsfElectrons")
process.electronMVAValueMapProducer.src = cms.InputTag("gedGsfElectrons")
process.photonMVAValueMapProducer.src = cms.InputTag("gedPhotons")
#process.electronRegressionValueMapProducer.src = cms.InputTag('reducedEgamma','gedGsfElectrons')
for idmod in electron_id_config.electron_ids.value():
    setupAllVIDIdsInModule(process,idmod,setupVIDElectronSelection)
for idmod in photon_id_config.photon_ids.value():
    setupAllVIDIdsInModule(process,idmod,setupVIDPhotonSelection)

process.load("CommonTools.RecoAlgos.sortedPFPrimaryVertices_cfi")
process.primaryVertexAssociation = process.sortedPFPrimaryVertices.clone(
    qualityForPrimary = cms.int32(2),
    produceSortedVertices = cms.bool(False),
    producePileUpCollection  = cms.bool(False),  
    produceNoPileUpCollection = cms.bool(False)
    )

#PAT Stuff
process.load('PhysicsTools.PatAlgos.producersLayer1.tauProducer_cff')
process.load('PhysicsTools.PatAlgos.producersLayer1.jetProducer_cff')
process.load('PhysicsTools.PatAlgos.producersLayer1.electronProducer_cff')
process.load('PhysicsTools.PatAlgos.producersLayer1.photonProducer_cff')
process.load('PhysicsTools.PatAlgos.producersLayer1.ootPhotonProducer_cff')
process.load('PhysicsTools.PatAlgos.producersLayer1.metProducer_cff')
process.load('PhysicsTools.PatAlgos.producersLayer1.muonProducer_cff')
process.makePatJetsTask.add(process.pfImpactParameterTagInfos, 
                            process.pfSecondaryVertexTagInfos,
                            process.pfInclusiveSecondaryVertexFinderTagInfos)

process.patCandidatesTask = cms.Task(
    process.makePatElectronsTask,
    process.makePatMuonsTask,
    #process.makePatTausTask,
    process.makePatPhotonsTask,
    process.makePatOOTPhotonsTask,
    process.makePatJetsTask,
    process.makePatMETsTask
    )
process.patCandidates = cms.Sequence(process.patCandidatesTask)


process.load('PhysicsTools.PatAlgos.selectionLayer1.tauSelector_cfi')
process.load('PhysicsTools.PatAlgos.selectionLayer1.jetSelector_cfi')
process.load('PhysicsTools.PatAlgos.selectionLayer1.electronSelector_cfi')
process.load('PhysicsTools.PatAlgos.selectionLayer1.muonSelector_cfi')
process.load('PhysicsTools.PatAlgos.selectionLayer1.photonSelector_cfi')
process.load('PhysicsTools.PatAlgos.selectionLayer1.ootPhotonSelector_cff')
process.selectedPatCandidatesTask = cms.Task(
    process.selectedPatElectrons,
    process.selectedPatMuons,
    #process.selectedPatTaus,
    process.selectedPatPhotons,
    process.selectedPatOOTPhotons,
    process.selectedPatJets
 )
process.selectedPatCandidates = cms.Sequence(process.selectedPatCandidatesTask)


process.load('PhysicsTools.PatAlgos.triggerLayer1.triggerProducer_cfi')
process.patTrigger.onlyStandAlone = cms.bool(False)
process.patTrigger.packTriggerLabels = cms.bool(False)
process.patTrigger.packTriggerPathNames = cms.bool(False)
process.patTrigger.packTriggerPrescales = cms.bool(True)

process.load('PhysicsTools.PatAlgos.slimming.selectedPatTrigger_cfi')
process.load('PhysicsTools.PatAlgos.slimming.slimmedPatTrigger_cfi')

process.patTask = cms.Task(
    process.patCandidatesTask,
    process.selectedPatCandidatesTask,
    #process.patTrigger,
    #process.selectedPatTrigger,
    #process.slimmedPatTrigger
)

process.load('EventFilter.CSCRawToDigi.cscUnpacker_cfi')
process.muonCSCDigis.InputObjects = 'rawDataCollector'

process.RECOSIMoutput = cms.OutputModule("PoolOutputModule",
    dataset = cms.untracked.PSet(
        dataTier = cms.untracked.string('RECOSIM'),
        filterName = cms.untracked.string('')
    ),
    fileName = cms.untracked.string('file:step2.root'),
    #outputCommands = process.RECOSIMEventContent.outputCommands,
    outputCommands = process.FEVTSIMEventContent.outputCommands,
    splitLevel = cms.untracked.int32(0)
)

#Define Execution Paths
process.outputPath = cms.EndPath(process.output)
#process.p = cms.Path( process.muonCSCDigis * process.primaryVertexAssociation * process.egmGsfElectronIDSequence * process.egmPhotonIDSequence * process.NjettinessAK8CHS * process.metFilters * process.ntuples )
process.p = cms.Path( process.primaryVertexAssociation * process.egmGsfElectronIDSequence * process.egmPhotonIDSequence * process.NjettinessAK8CHS * process.metFilters * process.ntuples )
process.RECOSIMoutput_step = cms.EndPath(process.RECOSIMoutput)

process.schedule = cms.Schedule(process.p)

#Add PAT tasks for jet Toolbox to execution schedule
process.schedule.associate(process.patTask)
from PhysicsTools.PatAlgos.tools.helpers import associatePatAlgosToolsTask
associatePatAlgosToolsTask(process)

## PU JetID
process.load("RecoJets.JetProducers.PileupJetID_cfi")
process.patTask.add(process.pileUpJetIDTask)
process.patJets.userData.userFloats.src = [ cms.InputTag("pileupJetId:fullDiscriminant"), ]
process.patJets.userData.userInts.src = [ cms.InputTag("pileupJetId:fullId"), ]

process.patJets.discriminatorSources = cms.VInputTag(
    cms.InputTag("pfJetBProbabilityBJetTags"),
    cms.InputTag("pfJetProbabilityBJetTags"),
    cms.InputTag("pfTrackCountingHighEffBJetTags"),
    )
process.patJets.addTagInfos     = cms.bool(True)
process.patJets.tagInfoSources  = cms.VInputTag( 'pfImpactParameterTagInfos'
                                                 ,'pfSecondaryVertexTagInfos'
                                                 ,'pfInclusiveSecondaryVertexFinderTagInfos')
process.patJets.addGenPartonMatch   = cms.bool(False)
process.patJets.embedGenPartonMatch = cms.bool(False)
process.patJets.genPartonMatch      = ''
process.patJets.addGenJetMatch      = cms.bool(False)
process.patJets.embedGenJetMatch    = cms.bool(False)
process.patJets.genJetMatch         = ''
process.patJets.getJetMCFlavour    = cms.bool(False)
process.patJets.addJetFlavourInfo  = cms.bool(False)
process.patJets.JetPartonMapSource = ''
process.patJets.JetFlavourInfoSource = ''
process.patMETs.addGenMET           = False
process.patMETs.genMETSource        = ''
