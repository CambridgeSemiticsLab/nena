const configData = {
 "captions": {
  "title": "NENA phono search"
 },
 "name": "nena",
 "description": "\n<p>Phonetic search interface for the Northeastern Neo-Aramaic Text-Fabric Corpus.</p>\n<p>Based on <a href=\"https://github.com/CambridgeSemiticsLab/nena_tf\" target=\"_blank\">NENA data in Text-Fabric format</a>.</p>\n<p>See the\n<a href=\"https://github.com/CambridgeSemiticsLab/nena_tf/blob/master/docs/features.md\" target=\"_blank\">data documentation</a>.</p>\n<p>This is a standalone app. You download it to your computer, and then it works without\nconnection to the internet.</p>\n<p>This web app is by:</p>\n<ul>\n<li> <a href=\"https://www.ames.cam.ac.uk/people/professor-geoffrey-khan\" target=\"_blank\">Geoffrey Khan</a> (initiator)\n<li> <a href=\"https://www.linkedin.com/in/cody-kingham-1135018a\" target=\"_blank\">Cody Kingham</a> (corpus developer)\n<li> <a href=\"https://pure.knaw.nl/portal/en/persons/dirk-roorda\" target=\"_blank\">Dirk Roorda</a> (software developer)\n</ul>\n",
 "containerType": "sentence",
 "simpleBase": false,
 "ntypes": [
  "word",
  "sentence",
  "line",
  "text"
 ],
 "ntypesinit": {
  "dialect": 539379,
  "text": 713308,
  "paragraph": 578369,
  "line": 575825,
  "sentence": 578719,
  "subsentence": 688811,
  "inton": 539381,
  "stress": 595045,
  "word": 713434,
  "letter": 1
 },
 "ntypessize": {
  "dialect": 2,
  "text": 126,
  "paragraph": 350,
  "line": 2544,
  "sentence": 16326,
  "subsentence": 24497,
  "inton": 36444,
  "stress": 93766,
  "word": 120151,
  "letter": 539378
 },
 "dtypeOf": {
  "sentence": "word",
  "line": "sentence",
  "text": "line"
 },
 "utypeOf": {
  "word": "sentence",
  "sentence": "line",
  "line": "text"
 },
 "visible": {
  "word": {
   "lang": false,
   "speaker": false,
   "text": true,
   "full": false,
   "fuzzy": true,
   "lite": false,
   "pos": false,
   "cls": false,
   "voice": false,
   "place": false,
   "manner": false
  },
  "line": {
   "number": false
  },
  "text": {
   "title": false,
   "dialect": false,
   "tid": false,
   "place": false
  }
 },
 "levels": {
  "word": "Some words are affixed to others without intervening space.",
  "sentence": "Sentences are delimited by full stops.",
  "line": "Lines are really paragraphs.",
  "text": "Texts are stories, having some metadata, consisting of lines."
 },
 "layers": {
  "word": {
   "lang": {
    "valueMap": {
     "1": "NENA",
     "2": "K.",
     "3": "A.",
     "4": "K./A.",
     "5": "A.|A.|K.",
     "6": "A.|K.",
     "7": "K./T.",
     "8": "K.|K.",
     "9": "K.|K.|K.",
     "10": "A.|A.",
     "11": "Urm.",
     "12": "E.",
     "13": "K./A./E.",
     "14": "P.",
     "15": "A./K.",
     "16": "K./A.|K./A.",
     "17": "T.",
     "18": "Ṭiy.",
     "19": "A./E.",
     "20": "K./E.",
     "21": "K./T.|K./T.",
     "0": ""
    },
    "pos": "lang",
    "pattern": "",
    "description": "language, indicated by a number"
   },
   "speaker": {
    "valueMap": {
     "1": "Dawið ʾAdam",
     "2": "Yulia Davudi",
     "3": "Yuwarəš Xošăba Kena",
     "4": "Manya Givoyev",
     "5": "Yuwəl Yuḥanna",
     "6": "Nanəs Bənyamən",
     "7": "Yosəp bet Yosəp",
     "8": "Yonan Petrus",
     "9": "Natan Khoshaba",
     "10": "Arsen Mikhaylov",
     "11": "Xošebo ʾOdišo",
     "12": "Nancy George",
     "13": "Awiko Sulaqa",
     "14": "Maryam Gwirgis",
     "15": "Alice Bet-Yosəp",
     "16": "Bənyamən Bənyamən",
     "17": "MB",
     "18": "Mišayel Barčəm",
     "19": "Nadia Aloverdova",
     "20": "Frederic Ayyubkhan",
     "21": "Victor Orshan",
     "22": "Merab Badalov",
     "23": "Sophia Danielova",
     "24": "Blandina Barwari",
     "25": "YD",
     "26": "Dawið Gwərgəs",
     "27": "Gwərgəs Dawið",
     "28": "AB",
     "29": "Jacob Petrus",
     "30": "Dawid Adam",
     "31": "NK",
     "32": "YP",
     "33": "JP",
     "34": "Kena Kena",
     "35": "Nawiya ʾOdišo",
     "36": "GK",
     "37": "Leya ʾOraha",
     "0": ""
    },
    "pos": "speaker",
    "pattern": "",
    "description": "speaker, indicated by a number"
   },
   "text": {
    "valueMap": null,
    "pos": "text",
    "pattern": "",
    "description": "text precise, complete, uses non-ascii: <code>maqəlbə̀nna</code>"
   },
   "full": {
    "valueMap": null,
    "pos": "full",
    "pattern": "",
    "description": "text representation: <code>maq9lb9`nna</code>"
   },
   "fuzzy": {
    "valueMap": null,
    "pos": "fuzzy",
    "pattern": "mute",
    "description": "text representation: <code>maqilbinna</code>"
   },
   "lite": {
    "valueMap": null,
    "pos": "lite",
    "pattern": "",
    "description": "text representation: <code>maq9lb9nna</code>"
   },
   "pos": {
    "valueMap": {
     "n": "NOUN",
     "pt": "PART",
     "pn": "PRON",
     "nr": "NUMR",
     "aj": "ADJV",
     "ab": "ADVB",
     "m": "MODI",
     "i": "INTJ",
     "pp": "PREP",
     "v": "VERB",
     "n|pt": "NOUN|PART",
     "n|n": "NOUN|NOUN",
     "pn|pt": "PRON|PART",
     "pt|pn": "PART|PRON",
     "m|n": "MODI|NOUN",
     "m|pn": "MODI|PRON",
     "pt|n": "PART|NOUN",
     "ab|n": "ADVB|NOUN",
     "n|ab": "NOUN|ADVB",
     "n|aj": "NOUN|ADJV",
     "aj|aj": "ADJV|ADJV",
     "aj|n": "ADJV|NOUN",
     "nr|nr": "NUMR|NUMR",
     "aj|ab": "ADJV|ADVB",
     "n|intj": "NOUN|INTJ",
     "n|n|n": "NOUN|NOUN|NOUN",
     "pt|pt|pt": "PART|PART|PART",
     "aj|n|n": "ADJV|NOUN|NOUN",
     "aj|n|n|n": "ADJV|NOUN|NOUN|NOUN",
     "n|n|n|n": "NOUN|NOUN|NOUN|NOUN",
     "z": ""
    },
    "pos": "pos",
    "pattern": "",
    "description": "part-of-speech"
   },
   "cls": {
    "valueMap": {
     "V": "vowel",
     "C": "consonant",
     "z": ""
    },
    "pos": "cls",
    "pattern": "",
    "description": "phonetic class: <code>CVCVCCVCCV</code>"
   },
   "voice": {
    "valueMap": {
     "P": "plain",
     "H": "unvoiced_aspirated",
     "V": "voiced",
     "F": "unvoiced",
     "G": "unvoiced_unaspirated",
     "X": "emphatic",
     "z": ""
    },
    "pos": "cls",
    "pattern": "",
    "description": "phonation: <code>PzzzPVzPPz</code>"
   },
   "place": {
    "valueMap": {
     "D": "dental-alveolar",
     "B": "labial",
     "C": "palatal-alveolar",
     "J": "palatal",
     "G": "velar",
     "X": "uvular",
     "Q": "pharyngeal",
     "H": "laryngeal",
     "z": ""
    },
    "pos": "cls",
    "pattern": "",
    "description": "phonation: <code>BzXzDBzDDz</code>"
   },
   "manner": {
    "valueMap": {
     "A": "affricative",
     "N": "nasal",
     "X": "other",
     "F": "fricative",
     "L": "lateral",
     "S": "sibilant",
     "z": ""
    },
    "pos": "cls",
    "pattern": "",
    "description": "phonation: <code>NzAzLAzNNz</code>"
   }
  },
  "line": {
   "number": {
    "valueMap": null,
    "pos": "number",
    "pattern": "",
    "description": "line number"
   }
  },
  "text": {
   "title": {
    "valueMap": null,
    "pos": "title",
    "pattern": "A",
    "description": "title of a text"
   },
   "dialect": {
    "valueMap": null,
    "pos": "dialect",
    "pattern": "",
    "description": "dialect of a text <code>Barwar Urmi_C</code>"
   },
   "tid": {
    "valueMap": null,
    "pos": "tid",
    "pattern": "",
    "description": "id of a text"
   },
   "place": {
    "valueMap": null,
    "pos": "place",
    "pattern": "Dure",
    "description": "place of a text"
   }
  }
 }
}