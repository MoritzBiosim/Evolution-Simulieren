Struktur der sandbox

Es gibt eine Welt (grid), in der sich Objekte (Stone, Food oder Pixies) befinden

Die Pixies werden gesteuert von Genomen, welche eine fixe Anzahl an Genen beinhalten
Die Gene wiederum manifestieren eine Connection zwischen zwei Funktionen/Neuronen: sensory/Neuron, Neuron/Neuron, sensor/Action oder Neuron/Action
	
	Möglichkeit 1: Leichter, ohne Mutationen
	Ein Gen hat eine zufällig festgelegt Connection (wie oben) und einen festen weight-Wert.

	Möglichkeit 2: Komplizierter, mit Mutation & Hamming-distance
	Ein Gen ist eine 32-bit-Binärzahl, die nach einem festgelegten Schlüssel zu einem Gen aus der Funktionenliste korreliert.
	Dafür sind diverse mapping- und Umrechnungsschritte notwendig (aber wurde alles schonmal von uns gecoded).
	Das Gen könnte dann für den Rest der Generation als Objekt wie in Möglichkeit 1 gespeichert werden.
	Dafür sind einzelne Mutationen an jedem bit möglich, und eine Hamming-distance ist berechenbar.

Soweit so einfach: Der schwierigste Schritt ist die Verlinkung von sensory und Action Neurons über die inner Neurons.

	Möglichkeit 1: Leichter, mit reduzierter Komplexität
	Inner Neurons werden gekickt, es gibt nur direkte Verbindungen zwischen sensor und action-Neuronen

	Möglichkeit 2: Schwieriger, mit mehr Möglichkeit für komplexes emergentes Verhalten
	Inner Neurons bilden eine Zwischenebene, die sich auch selbst wieder ansteuern können.
	Dabei summiert ein inner Neuron alle Inputwerte (zwischengespeichert in einer Liste o.ä.) und gibt einen Wert zwischen -1/1 aus.
	Der Outputwert wird im Neuron-Objekt selbst gespeichert
	Die Inputliste wird gecleart und neu mit dem outputwert des jetzigen Simsteps gefüllt. Dabei wird (z.B. als Tupel) sowohl das Ziel-Neuron (Nummer?)
	als auch der übergebene Wert gespeichert, so kann ein Inner Neuron sich auch selbst im nächsten Simstep ansteuern

	Möglichkeit 3: Komplett Objektorientiert
	Die Connections sind Objekte, die "Sensors", "Internals" und "Actions" sind eigene Klassen.
	Achtung: Jedes Pixie muss dabei eigene Objekte jeder im Genom kodierten Neuron-Klasse haben, damit individuelle input- und output-Werte 
	gespeichert werden können.
	Dabei verkörpert jedes Neuron nur eine einzige Verhaltensschleife (--> functionality) und speichert die eigenen Input/output-Werte.
	Bei jedem Simstep wird der Input-Wert (falls gegeben) verarbeitet und der output-Wert (falls vorhanden) an das vorgeschriebene Neuron als neuer
	Input-Wert weitergeleitet.
	Manche Input-Werte werden so erst im nächsten Simstep verarbeitet, aber wenn sensor- und action-Neuronen in der richtigen Reihenfolge aufgerufen
	werden sollte es auch noch im selben Simstep passieren können.
	Achtung 2: Inputwerte sollen im gleichen Simstep summiert werden, aber nicht über mehrere simSteps hinweg. Dafür sollen z.B. Internal Neurons
	aber schon ihre Output-Werte als Input-Werte im nächsten Schritt behalten können (evtl. über einen Zwischenspeicher).

Für die Übersichtlichkeit können verschiedene Teile der Simulation in verschiedenen Dateien zwischengespeichert werden:

	Obwohl ne wird schwierig, weil z.B. action-Neuronen Funktionen aufrufen müssen, die sich auf die Hauptwelt zurückbeziehen


queueForMove: der moveX/Y-Wert wird jede Runde getracked und zum Schluss des simSteps automatisch in Bewegung umgesetzt (sofern nicht (0,0))


um zu checken welche Verbindungen invalide sind:
- Verbindungen ohne Output sollen gekickt werden
	dafür wird für jede function im Sources-set geschaut, falls es ein internal Neuron ist (if in internal_dict.values() sollte gehen), ob es in der internal->internal oder internal->Action Liste einen Neurolink gibt der die Funktion als source hat

- inner Neurons die nur sich selbst ansteuern sollen gekickt werden
	dafür wird für jedes internal Neuron (if in internal_dict.values()) geschaut, ob es in der internal->Action Liste einen Neurolink mit der Funktion als source hat. Wenn nicht wird es removed

- das funktioniert nicht bzw. ist viel zu umständlich. Alternative: Wie D.Miller in jeder Funktion die variable "numOutputs", ("numInputs") und "numSelfInputs" tracken und anhand dessen entscheiden, welche Neuronen fliegen müssen.
Dafür muss einmal durch die source-bzw. sink-Liste iteriert werden und geschaut werden, was die neurolinks für sachen drin haben:
	- für jedes Neuron, das im source-Teil des neurolinks vorkommt, wird numOutputs erhöht.
	- für jedes Neuron, das im sink-Teil vorkommt, wird numInputs erhöht.
	- falls source und sink des neurolinks das gleiche Objekt ist, wird zusätzlich numSelfInputs erhöht.



Statt dass das Objekt beim Aufrufen des Neurolinks instanziert wird, erst mal nur Klasse speichern
Für jedes Klassen objekt im Set in einem NEUEN set/liste ein objekt instanzieren --> individuelles Neuron
Auf dieses Neuron (1 uniques pro Pixie) kann sich dann bezogen werden


Problem: Da internal Neurone sowohl im sink- als auch im source-set instanziert werden, existieren sie als zwei unterschiedliche Objekte. Deshalb wird numOutputs z.B. auch doppelt gezählt. Das ist aber natürlich auch blöd wenn sich Interneurone selbst ansteuern wollen.


Ich möchte schauen,
	-welche neurolinks ich habe, für jedes neurolink
		-ermitteln was der source ist, auf das source-OBJEKT zugreifen (kein neues Objekt instanzieren)



Also es kommt manchmal noch dieser Error: 
File "c:\Users\ochse\Evolution-Simulieren\Biosim_sandbox.py", line 515, in executeGenes
    sink_obj.input += internal_output
TypeError: unsupported operand type(s) for +=: 'NoneType' and 'float'

was bedeutet dass in dieser Zeile:
            sink_obj = next((obj for obj in self.sinkNeurons if obj.__class__ == i_i_neurolink.sink), None)
kein Objekt für obj.__class__ == ...sink gefunden wird und stattdessen None zurückgegeben wird.

Das kann daran liegen, dass sinkNeurons und i_i_neurolink.sink nicht auf dem gleichen Stand sind, oder dass der Link versucht eine Connection anzusteuern die es eigentlich gar nicht mehr geben dürfte (weil der sink schon gelöscht wurde). In dem Fall muss ich schauen dass das neural network sauberer aufgeräumt wird. Jetzt geh ich erstmal kacken


Wenn entweder die sourceNeurons-Liste oder die sinkNeurons-Liste leer ist, kann man davon ausgehen, dass es kein funktionierendes Genom gibt.
Dann könnte ein Bool functioningGenome = False gesetzt werden, und der executeGenome-Schritt übersprungen werden. Das Pixie macht dann einfach gar nichts.


Im Moment wird das Genom in 6 Schritten "exprimiert", wobei auf jeder Ebene alle Neurone (falls vorhanden) abgegriffen werden und ausgeführt.
	--> das ganze funktioniert über for-Schleifen, die durch Listen iterieren

Alternativ könnte man auch einen mehr "kanalisierten" Approach nehmen, der eventuell Fehleranfälliger ist, aber andererseits flexibel ist bezüglich der Länge der computeten Genome (wenn z.B. mehrere Internal Neurons auftreten).
Dafür würde nur auf der obersten Ebene (Sensors) durch die Liste iteriert werden und jeder Output weitergeleitet werden bis zu einem Action Neuron bzw. einem Internal Neuron das sich selbst feedet. Ganz zum Schluss (muss halt erkannt werden, wann Schluss ist) werden erst alle Action Neurone ausgeführt.
Das ganze hat ein bisschen was von rekursivem Coding, aber könnte ganz elegant werden. Würde dann so ablaufen:

1. ein Sensor-Neuron gibt einen Output aus
2. In der s->i-Liste wird geschaut, welche Neurolinks das Neuron als source haben und diese transferieren den Output dann auch

	a) wenn das Sink-Neuron ein Internal Neuron ist (das nicht das Source-Neuron ist), wird das Neuron executed und der Output wieder in Schritt 2. in das sink-Neuron eingespeist
	b) andernfalls handelt es sich automatisch um ein Action Neuron oder ein self-linking Internal Neuron, der Output wird weitergeleitet und die loop wird gestoppt.
3. Alle Action Neuronen werden executed

^Problem damit: Bei jedem sensor-Neuron werden alle nachfolgenden internal Neurons sofort ausgeführt, ohne auf den Input anderer Neurone zu warten!

Andere, unkonventionelle Möglichkeit:
Wir tracken ja bei jedem Neuron die numInputs. Wir können daher jeden simStep einfach tracken, ob die benötigte Anzahl an Inputs = numInputs-numSelfInputs erreicht wurde (indem bei jedem Input der Tracker eins hochgemacht wird), und wenn ja das Neuron AUTOMATISCH ausführen, ohne dass es dafür von extern einen command bräuchte.
Auch action-Neurone können sofort ausgeführt werden, weil heikle Operationen wie move() ja sowieso gequeuet werden und erst am Ende des simSteps ausgeführt werden.
Nach jedem execute muss der inputTracker wieder auf 0 gesetzt werden!! und die Inputs selber auch.

Dafür müssen in der mainloop nur die sensorNeurons ausgeführt werden.

Dafür wäre es auch praktisch, wenn jedes (sensor/internal)Neuron selber wüsste, an wen es seine Outputs weiterleiten muss:
Am Anfang in der loadGenome-Funktion könnte durch die genes-Liste iteriert werden und jeder neurolink, der einem instanzierten Neuron als source entspricht, wird einem Attribut ownSinks oder so zugeordnet werden. Dann kann ein Neuron, wenn es executed wird, selbstständig den eigenen Output an alle sinks in der ownSinks-Liste weiterleiten (und natürlich immer schön den input-Tracker erhöhen) --> Problem: in den neurolinks werden ja keine Objekte, sondern Klassen gespeichert. In der ownSinks-Liste müssen aber Objekte stehen, ALSO muss während der loadGenome-Phase nicht der Neurolink selber zugeordnet werden, sondern das Neuron aus der sinkNeurons-Liste, das der Klasse des neurolink.sink entspricht. Voilá!


Ich hab total vergessen die weights einzubauen. Die Information geht auch verloren im Laufe von loadGenome, weil die Info, an welche sink-Neurons der Output übertragen werden soll komplett von den neurolinks entkoppelt wird. Als Lösung müsste die weight für jede Verbindung mit übergeben werden. 
Aber das ist nicht schwer: Jedes sink-objekt wird ja einzeln zu ownSinks[] hinzugefügt. Statt einzelne Objekte zu übergeben kann einfach ein Tupel mit (sink_obj, weight) übergeben werden - dann muss das Neuron bei transferOutputs nur das korrespondierende ownSinks[0]-Neuron ansteuern und den Output mit ownSinks[1] multiplizieren.

Super, das funktioniert alles!


Nächster Schritt: 
- eine function schreiben, die für jedes Pixie jeden simStep ausgeführt wird:
	- das Genom soll ausgeführt werden
	- gequeuete Funktionen (z.B. moveX, moveY) sollen ausgeführt werden 
		- dafür wird jedes mal, wenn eine move-Funktion ausgeführt wird, das Pixie dem world.queueForMove -set hinzugefügt. Dann kann am Schluss des simsteps über dieses set iteriert werden (in zufälliger Reihenfolge, dann ist es sogar fair :^) ) und für alle Pixies darin die move-Funktion ausgeführt werden. Das gleiche mit nem anderen set für andere queue-Funktionen wie kill etc.

Erledigt👍

Als nächstes sollen Pixies prozedural gespawnt werden können.
Das sollte nicht so schwer sein, das kann ich fast genauso machen wie bei PredatorPrey.
Zusätzlich könnte ich an einer "Vererbungs"-Funktion arbeiten, die random Pixies aus world.inhabitants nimmt, ihre DNA kopiert und neue (in einer neuen world) Pixies instanziert, mit der DNA des vorherigen Pixies, und zwar so viele wie defaultNumPixies (es wird also immer wieder aufgefüllt). Die alte world oder zumindest seine .inhabitants und .Environment-Liste sollte nach Möglichkeit gelöscht werden, damit Speicherplatz freigegeben wird (safe nützlich bei langen Simulationen)


#######
To Do: Es wäre cool einen Weg zu haben die Farbe eines Pixies abhängig vom Genom zu machen, d.h. von der DNA.
Dabei muss der 32bit-string irgendwie in eine Farbe umgewandelt werden. Good to know: Unser 32bit string kodiert 4294967296 Zahlen, ein Hexcode (FFFFFF) nur 16^6=16777216 Zahlen, d.h. der 32bit-string kodiert 256 mal mehr Zahlen. Der gesamte 32bit-code könnte also als integer interpretiert, durch 256 geteilt werden und in Hexcode-Format umgeschrieben werden um eine unique Zahl zu bekommen (Problem: bits hinter der 8. Stelle sind dabei so gut wie irrelevant).
Als Workaround könnte der 32bit-string in 4 Teile á 8 bits geteilt werden, die ersten drei (die letzen 8 Ziffern sind auch für das Pixie recht irrelevant) ergeben je eine Zahl zwischen 0 und 255 die als RGB-Wert gezählt werden kann. Nun könnte der Durchschnitt der Farben aller Gene für die Farbe des Pixies genommen werden. Problem: dann sind wahrscheinlich alle braun.
Also hier muss noch was besseres ausgetüftelt werden
--> z.B. dass bei jeder Mutation tatsächlich eine random Stelle vom Hexcode mutiert wird (radikal)



Um kontrolliert Populationen testen zu können, braucht es einen Weg, Die Genome aller inhabitants (vor dem selektieren) zu speichern und an anderer Stelle wieder einzufüttern (z.B. bei firstGeneration()) --> check!

Orientierung des Pixies tracken - "facing"-variable
	- eine Möglichkeit wäre, die facing-Variable als Vektor des letzten Movements zu tracken
		- wenn "moveForward" getriggert wird, wird einfach derselbe Vektor als movement-urge übergeben
		- wenn "moveBackwards" getriggert wird, wird das Vorzeichen von jedem element umgedreht.
		- wenn "moveLeft"/"moveRight" getriggert wird, wird es komplizierter.
	- andere Möglichkeit wäre, die facing-Variable als Winkel (rad) des letzten movements zu tracken. Dann müsste bei jedem move der Winkel zuerst in eine Richtung übersetzt werden und dieser dann an die movement-urge variable übergeben.
		- wenn moveForward getriggert wird, wird die aktuelle facing-variable in einen Vektor übersetzt
		- wenn moveBackwards getriggert wird, wird 1*pi draufgerechnet und dann in einen vektor übersetzt
		- bei moveRight/Left wird jeweils pi/2 draufgerechnet bzw. abgezogen.
Dafür brauchen wir eine Function, die Vektoren in Winkel übersetzt: getRelativeAngle braucht Vector Argument
Und eine Function, die Winkel in Vektoren übersetzt: getNormalizedDirection braucht winkel Argument



Könnte es sogar SEX geben??? Hierbei müssen zwei Pixies, die sich treffen und zufällig sex "initiieren", z.B. die Hälfte aller .genes austauschen. Das hat keine Auswirkungen auf das neural network des betroffenen Pixies, aber auf die des nächsten Erben
Wäre aber gut wenn man sex auf 1 mal pro Generation limitiert.
--> Damit könnten wir Mullers Ratchet umgehen bzw. den "Ruby in the rubbish" finden!


Es fehlt noch ein searchRadius-Argument für searchNeighbourhood etc., die sich nicht auf defaultsearchRadius (existiert nicht mehr!) bezieht
--> fixed


#######
Können wir die Neuron-classes auslagern?
	- die neuron_dicts müssten auf jeden Fall im alten Dokument bleiben, aber statt der 0: moveN - Schreibweise könnte es dann 0: neurons.moveN heißen - eigentlich sollte Python das gut erkennen sollen
	- hoffentlich funktionieren dann auch die ganzen compare-Funktionen noch (wie Neuron.__class__ == neurolink.source), das könnte man aber gut in nem anderen Dokument testen
	- die Objekte werden von der loadGenomes-Funktion instanziert und sofort einer Liste zugeordnet, das heißt sie sollten auch in der main Datei existieren
	- Letzte Frage bleibt, ob die execute-Funktionen in den Objekten, die sich auf Objekte des genomes/des pixies/der world etc. beziehen (z.B. xPosition das dann noch korrekt referenzieren können, aber das müsste theoretisch auch kein Problem sein solange diese Sachen bei der Instanzierung mit übergeben werden, und das werden sie ja mit attributedPixie.


ToDo:
- oldDNA tracken? D.h. wenn eine DNA-Mutation passiert, wird die alte beim genome abgespeichert. oldDNA wird auch bei Vererbung mit vererbt
- Überlebensrate & Diversität jede Generation tracken und in Tabelle speichern
	- Überlebensrate: len(inhabitants) nach applySelectioCriteria / numPixies
	- Diversität: Schwieriger, dafür muss im Prinzip die DNA aller inhabitants einem Set zugeordnet werden und dann len(set) / numPixies
		aber: wenn Mutationen erlaubt, kann das zu trügerisch hoher Diversität führen. Als Workaround könnte die Hamming distance für jedes set untereinander ausgerechnet werden und wenn zwei sehr nah sind nur als eins gezählt werden, oder komplizierter es werden die Verbindungen + Vorzeichen des weights ausgewertet. Das könnte aber wirklich viel code in Anspruch nehmen

Testen:
- Überprüfen ob Internal Neurons wirklich funktionieren: Speichern sie ihre alten Outputs als Inputs und verwenden sie im nächsten Simstep wieder?
- Funktioniert mutateGenes? ja


Bei D. Miller gibt es auch Internal Neurons, die ohne Input funktionieren (obwohl er im Video sagt, dass alles was sie machen ist Inputs zu summieren). Man könnte also überlegen ob man ihnen Default Output werte gibt die sie raushauen wenn sie keinen Input bekommen. Dafür müsste man auch deaktivieren dass I. Neurons entfernt werden wenn sie keine Input Connections haben. Oder man lässts
--> Das würde aber zu integrierten On/Off-Schaltern führen, weil wenn sich ein Neuron einmal selber ansteuert (und/oder keine sonstigen Inputs erhält), gibt es immer denselben Wert aus - bzw. der Wert schrumpft kontinuierlich, weil eine tanh-Funktion keinen Fixpunkt hat


AbsNeuron / PosNeuron als "Hochpassfilter": Gibt nur Output aus, wenn Input > 0, sonst 0. 
	-->AbsNeuron könnte auch negative Werte annehmen und immer de Betrag outputten


Funktion spawnFood(name, type, quantity, energyValue)
-> name kann irgendwas sein ("bananas", "food1")
-> type ist str , z.B. "random", "spread", "clumped". Jeder type generiert food-Verteilung auf andere weise, wie aus Öko VL
-> quantity sagt wie viele food-Objekte insgesamt generiert werden
-> energyValue sagt wie viel energy man von jedem food-item kriegt