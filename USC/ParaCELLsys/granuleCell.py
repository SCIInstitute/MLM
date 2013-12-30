import random # each cell should have a random number generator

class granuleCell:
    def __init__(self, morphFileName, cellID, synapseCount, locn, parent, synvars):
        # The following lists are to split the dendritic tree into the inner, middle, and outer third layers.
        self.synvars = synvars
        self.granuleCellLayer = []
        self.innerThird = []
        self.middleThird = []
        self.outerThird = []
        # Since all the morphology is defined by HOC code, we need a pointer to the HOC object.
        self.c = h.mkcell(morphFileName)
        self.morphFileName = morphFileName
        # Set the cell ID.
        self.ID = cellID
        # Initialize the random number generator with the ID as the fixed seed (so we can reproduce the results).
        self.ranGen = random.Random()
        self.ranGen.seed(cellID)
        # Initialize the list of synapses for the cell
        self.allSyns = []
        # Initialize the list of NetCons for the cell
        self.nc_list = []

        # Set the location.  This is a tuple (immutable list).
        self.location = locn

        self.synapseCount = [self.ranGen.randint(synapseCount[0][0], synapseCount[0][1]),
                             self.ranGen.randint(synapseCount[1][0], synapseCount[1][1]),
                             self.ranGen.randint(synapseCount[2][0], synapseCount[2][1])]

        # Set parent region.  This is a class of type Post_Cell_SubR
        self.parentRegion = parent

        # We need a data structure to keep track of which input cells (EC) have created synapses, and how many times.
        self.inputCellSyns = {}

        # Which bin does the cell belong to?
        self.bin = -1

        # Set the maximum number of times any given input cell can synapse onto me.
        self.maxSynapticConnectionsPerCell = 1000

        # Find farthest extent of dendritic tree from cell body (along z axis), so we can divide the sections.
        self.values = []
        for i in range(len(self.c.dend)):
            self.c.dend[i].push()
            for j in range(int(h.n3d())):
                self.values.append(h.z3d(j))
            h.pop_section()
        self.maxExtent = max(self.values)

        # Then, categorize each dendritic section as belonging to either the inner, middle, or outer third.
        for i in range(len(self.c.dend)):
            self.values = []
            self.c.dend[i].push()
            for j in range(int(h.n3d())):
                self.values.append(h.z3d(j))
            mean = (min(self.values) + max(self.values)) / 2
            if min(self.values) == 0:
                self.granuleCellLayer.append(self.c.dend[i])
            elif mean < self.maxExtent / 3:
                self.innerThird.append(self.c.dend[i])
            elif mean < self.maxExtent * 2 / 3:
                self.middleThird.append(self.c.dend[i])
            else:
                self.outerThird.append(self.c.dend[i])
            h.pop_section()

        # Now, insert the proper biophysics for each section.
        # Rule for adding variability: mean value (from literature) +/- 5%
        self.var = 0.05
        for sec in self.c.all:
            sec.insert('ccanl')
            sec.catau_ccanl = 10 + self.ranGen.uniform(-self.var * 10, self.var * 10)
            sec.caiinf_ccanl = 5.0e-6 + self.ranGen.uniform(-self.var * 5.0e-6, self.var * 5.0e-6)
            sec.Ra = 410 + self.ranGen.uniform(-self.var * 410, self.var * 410)
            # We want each section to have more than one segment...
            # (Programming note: it's probably not good to hard-code nseg, but to use some rule-based assignment.)
            sec.nseg = 9

        for sec in self.c.somatic:
            sec.insert('ichan2')
            sec.gnatbar_ichan2 = 0.12 + self.ranGen.uniform(-self.var * 0.12, self.var * 0.12)
            sec.gkfbar_ichan2 = 0.016 * 2.25 + self.ranGen.uniform(-self.var * 0.016, self.var * 0.016)
            sec.gksbar_ichan2 = 0.006 + self.ranGen.uniform(-self.var * 0.006, self.var * 0.006)
            sec.insert('borgka')
            sec.gkabar_borgka = 0.012 + self.ranGen.uniform(-self.var * 0.012, self.var * 0.012)
            sec.insert('nca')
            sec.gncabar_nca = (0.002 + self.ranGen.uniform(-self.var * 0.002, self.var * 0.002)) / 1.36
            sec.insert('lca')
            sec.glcabar_lca = 0.005 + self.ranGen.uniform(-self.var * 0.005, self.var * 0.005)
            sec.insert('cat')
            sec.gcatbar_cat = 0.000037 * 70 + self.ranGen.uniform(-self.var * 0.000037, self.var * 0.000037)
            sec.insert('gskch')
            sec.gskbar_gskch = 0.001 + self.ranGen.uniform(-self.var * 0.001, self.var * 0.001)
            sec.insert('cagk')
            sec.gkbar_cagk = (0.0006 + self.ranGen.uniform(-self.var * 0.0006, self.var * 0.0006)) / 15
            sec.gl_ichan2 = 0.00004 + self.ranGen.uniform(-self.var * 0.00004, self.var * 0.00004)
            sec.cm = 1 + self.ranGen.uniform(-self.var * 1, self.var * 1)

        for sec in self.granuleCellLayer:
            sec.insert('ichan2')
            sec.gnatbar_ichan2 = 0.018 + self.ranGen.uniform(-self.var * 0.018, self.var * 0.018)
            sec.gkfbar_ichan2 = 0.004 + self.ranGen.uniform(-self.var * 0.004, self.var * 0.004)
            sec.gksbar_ichan2 = 0.006 + self.ranGen.uniform(-self.var * 0.006, self.var * 0.006)
            sec.insert('nca')
            sec.gncabar_nca = (0.003 + self.ranGen.uniform(-self.var * 0.003, self.var * 0.003)) / 1.36
            sec.insert('lca')
            sec.glcabar_lca = 0.0075 + self.ranGen.uniform(-self.var * 0.0075, self.var * 0.0075)
            sec.insert('cat')
            sec.gcatbar_cat = 0.000075 + self.ranGen.uniform(-self.var * 0.000075, self.var * 0.000075)
            sec.insert('gskch')
            sec.gskbar_gskch = 0.0004 + self.ranGen.uniform(-self.var * 0.0004, self.var * 0.0004)
            sec.insert('cagk')
            sec.gkbar_cagk = (0.0006 + self.ranGen.uniform(-self.var * 0.0006, self.var * 0.0006)) / 15
            sec.gl_ichan2 = 0.00004 + self.ranGen.uniform(-self.var * 0.00004, self.var * 0.00004)
            sec.cm = 1 + self.ranGen.uniform(-self.var * 1, self.var * 1)

        for sec in self.innerThird:
            sec.insert('ichan2')
            sec.gnatbar_ichan2 = 0.013 + self.ranGen.uniform(-self.var * 0.013, self.var * 0.013)
            sec.gkfbar_ichan2 = 0.004 + self.ranGen.uniform(-self.var * 0.004, self.var * 0.004)
            sec.gksbar_ichan2 = 0.006 + self.ranGen.uniform(-self.var * 0.006, self.var * 0.006)
            sec.insert('nca')
            sec.gncabar_nca = (0.001 + self.ranGen.uniform(-self.var * 0.001, self.var * 0.001)) / 1.36
            sec.insert('lca')
            sec.glcabar_lca = 0.0075 + self.ranGen.uniform(-self.var * 0.0075, self.var * 0.0075)
            sec.insert('cat')
            sec.gcatbar_cat = 0.00025 + self.ranGen.uniform(-self.var * 0.00025, self.var * 0.00025)
            sec.insert('gskch')
            sec.gskbar_gskch = 0.0002 + self.ranGen.uniform(-self.var * 0.0002, self.var * 0.0002)
            sec.insert('cagk')
            sec.gkbar_cagk = (0.001 + self.ranGen.uniform(-self.var * 0.001, self.var * 0.001)) / 15
            sec.gl_ichan2 = 0.000063 + self.ranGen.uniform(-self.var * 0.000063, self.var * 0.000063)
            sec.cm = 1.6 + self.ranGen.uniform(-self.var * 1.6, self.var * 1.6)

        for sec in self.middleThird:
            sec.insert('ichan2')
            sec.gnatbar_ichan2 = 0.008 + self.ranGen.uniform(-self.var * 0.008, self.var * 0.008)
            sec.gkfbar_ichan2 = 0.001 + self.ranGen.uniform(-self.var * 0.001, self.var * 0.001)
            sec.gksbar_ichan2 = 0.006 + self.ranGen.uniform(-self.var * 0.006, self.var * 0.006)
            sec.insert('nca')
            sec.gncabar_nca = (0.001 + self.ranGen.uniform(-self.var * 0.001, self.var * 0.001)) / 1.36
            sec.insert('lca')
            sec.glcabar_lca = 0.0005 + self.ranGen.uniform(-self.var * 0.0005, self.var * 0.0005)
            sec.insert('cat')
            sec.gcatbar_cat = 0.0005 + self.ranGen.uniform(-self.var * 0.0005, self.var * 0.0005)
            sec.insert('gskch')
            sec.gskbar_gskch = 0.0
            sec.insert('cagk')
            sec.gkbar_cagk = (0.0024 + self.ranGen.uniform(-self.var * 0.0024, self.var * 0.0024)) / 15
            sec.gl_ichan2 = 0.000063 + self.ranGen.uniform(-self.var * 0.000063, self.var * 0.000063)
            sec.cm = 1.6 + self.ranGen.uniform(-self.var * 1.6, self.var * 1.6)

        for sec in self.outerThird:
            sec.insert('ichan2')
            sec.gnatbar_ichan2 = 0.0
            sec.gkfbar_ichan2 = 0.001 + self.ranGen.uniform(-self.var * 0.001, self.var * 0.001)
            sec.gksbar_ichan2 = 0.008 + self.ranGen.uniform(-self.var * 0.008, self.var * 0.008)
            sec.insert('nca')
            sec.gncabar_nca = (0.001 + self.ranGen.uniform(-self.var * 0.001, self.var * 0.001)) / 1.36
            sec.insert('lca')
            sec.glcabar_lca = 0.0
            sec.insert('cat')
            sec.gcatbar_cat = 0.001 + self.ranGen.uniform(-self.var * 0.001, self.var * 0.001)
            sec.insert('gskch')
            sec.gskbar_gskch = 0.0
            sec.insert('cagk')
            sec.gkbar_cagk = (0.0024 + self.ranGen.uniform(-self.var * 0.0024, self.var * 0.0024)) / 15
            sec.gl_ichan2 = 0.000063 + self.ranGen.uniform(-self.var * 0.000063, self.var * 0.000063)
            sec.cm = 1.6 + self.ranGen.uniform(-self.var * 1.6, self.var * 1.6)

        for sec in self.c.all:
            sec.enat = 45 + self.ranGen.uniform(-self.var * 45, self.var * 45)
            sec.ekf = -90 + self.ranGen.uniform(-self.var * -90, self.var * -90)
            sec.eks = -90 + self.ranGen.uniform(-self.var * -90, self.var * -90)
            sec.ek = -90 + self.ranGen.uniform(-self.var * -90, self.var * -90)
            sec.elca = 130 + self.ranGen.uniform(-self.var * 130, self.var * 130)
            sec.etca = 130 + self.ranGen.uniform(-self.var * 130, self.var * 130)
            sec.esk = -90 + self.ranGen.uniform(-self.var * -90, self.var * -90)
            sec.el_ichan2 = -70 + self.ranGen.uniform(-self.var * -70, self.var * -70)
            sec.cao = 2 + self.ranGen.uniform(-self.var * 2, self.var * 2)

        # Next, we need to add the spines/synapses.
        for i in range(3):
            #k = self.ranGen.randint(synapseCount[i][0], synapseCount[i][1])
            k = self.synapseCount[i]
            for j in range(k):
                self.addSingleSynapse(i)
        # Add an inhibitory synapse.
        self.addSingleSynapse(3, inhib=True)

    def connect_pre(self, syn, wt, dly):
        # This function attaches my axon (or other generator of APs), to the synapse that's passed to me from
        # another cell.

        # The section of the cell that is going to be the AP generator has to be the currectly accessed section, so do that...
        self.c.soma[0].push()
        nc = h.NetCon(self.c.soma[0](1)._ref_v, syn, 0, dly, wt)
        #nc.threshold = 0
        #nc.weight[0] = wt
        #nc.delay = dly
        self.nc_list.append(nc)
        h.pop_section()
        return nc

    def addSingleSynapse(self, reg, inhib=False):
        # This function will create a single NEURON Exp2Syn synapse and add it to the cell's list
        # Syntax for new Exp2Syn is h.Exp2Syn(which section(location along section))
        region = [self.innerThird, self.middleThird, self.outerThird, self.c.soma]
        #syns = [self.innerSyn, self.middleSyn, self.outerSyn, self.somaSyn]
        #region = [self.c.somatic, self.c.somatic, self.c.somatic]
        #syns = [self.innerSyn, self.middleSyn, self.outerSyn]
        if len(region[reg]) > 0:
            if inhib:
                syn = h.Exp2Syn(region[reg][self.ranGen.randint(0, len(region[reg]) - 1)](self.ranGen.uniform(0, 1)))
                syn.tau1 = self.ranGen.uniform(.2, .3)
                syn.tau2 = self.ranGen.uniform(5.3, 5.7)
                syn.e = self.ranGen.uniform(-85, -70)
                #syns[reg].append(syn)
                self.allSyns.append(syn)
            else:
                if self.synvars['type'] == "E2":
                    syn = h.Exp2Syn(
                        region[reg][self.ranGen.randint(0, len(region[reg]) - 1)](self.ranGen.uniform(0, 1)))
                if self.synvars['type'] == "E2_Prob":
                    syn = h.E2_Prob(
                        region[reg][self.ranGen.randint(0, len(region[reg]) - 1)](self.ranGen.uniform(0, 1)))
                    syn.P = self.synvars['P']
                if self.synvars['type'] == "E2_STP_Prob":
                    syn = h.E2_STP_Prob(
                        region[reg][self.ranGen.randint(0, len(region[reg]) - 1)](self.ranGen.uniform(0, 1)))
                if self.synvars['type'] == "STDPE2":
                    syn = h.STDPE2(region[reg][self.ranGen.randint(0, len(region[reg]) - 1)](self.ranGen.uniform(0, 1)))
                if self.synvars['type'] == "STDPE2_Clo":
                    syn = h.STDPE2_Clo(
                        region[reg][self.ranGen.randint(0, len(region[reg]) - 1)](self.ranGen.uniform(0, 1)))
                if self.synvars['type'] == "STDPE2_STP":
                    syn = h.STDPE2_STP(
                        region[reg][self.ranGen.randint(0, len(region[reg]) - 1)](self.ranGen.uniform(0, 1)))
                if self.synvars['type'] == "STDPE2_Prob":
                    syn = h.STDPE2_Prob(
                        region[reg][self.ranGen.randint(0, len(region[reg]) - 1)](self.ranGen.uniform(0, 1)))
                    syn.P = self.synvars['P']
                #initializes different variables depending on synapse
                if (self.synvars['type'] == "STDPE2_STP") | (self.synvars['type'] == "E2_STP_Prob"):
                    syn.F1 = self.synvars['F1']
                if (self.synvars['type'] == "STDPE2_Clo" ) | ( self.synvars['type'] == "STDPE2_STP") | (
                    self.synvars['type'] == "STDPE2") | (self.synvars['type'] == "STDPE2_Prob"):
                    syn.wmax = self.synvars['wmax']
                    syn.wmin = self.synvars['wmin']
                    syn.thresh = self.synvars['thresh']
                if (self.synvars['type'] == "E2_Prob" ) | ( self.synvars['type'] == "E2_STP_Prob") | (
                    self.synvars['type'] == "STDPE2_STP") | (self.synvars['type'] == "STDPE2_Prob"):
                    h.use_mcell_ran4(1)
                    syn.seed = self.ranGen.randint(1, 4.295e9)
                syn.tau1 = self.synvars['t1_av'] + self.ranGen.uniform(-self.synvars['t1_range'] / 2,
                                                                       self.synvars['t1_range'] / 2)
                syn.tau2 = self.synvars['t2_av'] + self.ranGen.uniform(-self.synvars['t2_range'] / 2,
                                                                       self.synvars['t2_range'] / 2)
                syn.e = self.synvars['rev_av'] + self.ranGen.uniform(-self.synvars['rev_range'] / 2,
                                                                     self.synvars['rev_range'] / 2)
                #syns[reg].append(syn)
                self.allSyns.append(syn)
        else:
            # print "Whoops!  SectionList empty!"
            self.synapseCount[reg] = 0

#end code
