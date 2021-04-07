"""
Basic Language support checks
"""
import pytest
from hyperglot.languages import Languages
from hyperglot.language import Language


def test_language_supported():
    Langs = Languages()

    # A Language object with the 'fin' data
    fin = Language(Langs["fin"], "fin")

    # These "chars" represent a font with supposedly those codepoints in it
    fin_chars_missing_a = "bcdefghijklmnopqrstuvwxyzäöå"
    fin_chars_base = "ABCDEFGHIJKLMNOPQRSTUVWXYZÄÖÅabcdefghijklmnopqrstuvwxyzäöå"  # noqa
    fin_chars_aux = "ABCDEFGHIJKLMNOPQRSTUVWXYZÄÖÅÆÕØÜŠŽabcdefghijklmnopqrstuvwxyzäöåæõøüšž"  # noqa
    fin_chars_no_precomposed = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz ̈ ̊"  # noqa

    # This is what supported should look like if it determines 'fin' is
    # supported
    fin_matched = {"Latin": ["fin"]}

    # Note pruneOrthographies=False is used to re-use the same Language object
    # for these tests without having removed unsupported orthographies

    matches = fin.supported(fin_chars_base, pruneOrthographies=False)
    assert matches == fin_matched

    no_matches = fin.supported(fin_chars_base, level="aux",
                               pruneOrthographies=False)
    assert no_matches == {}

    matches = fin.supported(fin_chars_aux, level="aux",
                            pruneOrthographies=False)
    assert matches == fin_matched

    no_matches = fin.supported(fin_chars_base, level="aux",
                               pruneOrthographies=False)
    assert no_matches == {}

    no_matches = fin.supported(fin_chars_missing_a, pruneOrthographies=False)
    assert no_matches == {}


def test_language_inherit():
    Langs = Languages(inherit=True)

    # aae inherits aln orthography
    aae = Language(Langs["aae"], "aae")
    aln = Language(Langs["aln"], "aln")
    assert aae.get_orthography()["base"] == aln.get_orthography()["base"]

    # without inheritance aae's only orthography should not have any base chars
    Langs = Languages(inherit=False)
    aae = Language(Langs["aae"], "aae")
    assert "base" not in aae.get_orthography()


def test_language_preferred_name():
    Langs = Languages()
    bal = Language(Langs["bal"], "bal")
    #   name: Baluchi
    #   preferred_name: Balochi
    assert bal.get_name() == "Balochi"


def test_language_get_autonym():
    Langs = Languages()
    bal = Language(Langs["bal"], "bal")
    #   name: Baluchi
    #   - autonym: بلۏچی
    #     script: Arabic
    #   preferred_name: Balochi

    # For Arabic it should return the correct autonym, without script False
    assert bal.get_autonym(script="Arabic") == "بلۏچی"
    assert bal.get_autonym() is False


def test_language_all_orthographies():
    Langs = Languages()
    # smj Lule Sami with one primary and one deprecated orthography should
    # always return only the primary
    smj = Language(Langs["smj"], "smj")
    # All the chars from both orthographies
    smj_base = "A B C D E F G H I J K L M N O P Q R S T U V W X Y Z Á Ä Å Ñ Ö Ń a b c d e f g h i j k l m n o p q r s t u v w x y z á ä å ñ ö ń A B D E F G H I J K L M N O P R S T U V Á Ä Å Ŋ a b d e f g h i j k l m n o p r s t u v á ä å ŋ a n o ́ ̃ ̈ ̊"  # noqa

    # When checking primary orthographies only one should be included
    support = smj.supported(smj_base)
    assert ("smj" in support["Latin"]) is True
    assert len(smj["orthographies"]) == 1

    # Even when checking all orthographies the 'deprecated' orthography should
    # not be included
    support = smj.supported(smj_base, checkAllOrthographies=True)
    assert len(smj["orthographies"]) == 1

    # rmn Balkan Romani has Latin (primary) and Cyrillic orthographies
    # It should return only Latin by default, but both when listing all
    rmn = Language(Langs["rmn"], "rmn")

    # All the chars from both orthographies
    rmn_base = "A Ä Á B C Ć Č D E Ê É F Ğ H I Î Í J K L M N O Ö Ó P Ṗ Q R Ř S Š T U V W X Y Z a ä á b c ć č d e ê é f ğ h i î í j k l m n o ö ó p ṗ q r ř s š t u v w x y z А Б В Г Д Е Ё Ж З И Й К Л М Н О П Р С Т У Ф Х Ц Ч Ш Ы Ь Э Ю Я а б в г д е ё ж з и й к л м н о п р с т у ф х ц ч ш ы ь э ю я"  # noqa

    # When checking all orthographies, the Cyrillic non-primary should be
    # included
    support = rmn.supported(rmn_base, checkAllOrthographies=True)
    assert ("rmn" in support["Latin"]) is True
    assert ("Cyrillic" in support.keys()) is True
    assert len(rmn["orthographies"]) == 2

    # When checking only primary only Latin should be included
    support = rmn.supported(rmn_base, checkAllOrthographies=False)
    assert ("rmn" in support["Latin"]) is True
    assert ("Cyrillic" not in support.keys()) is True
    assert len(rmn["orthographies"]) == 1


def test_language_multiple_primaries():
    Langs = Languages()

    # E.g. aat Arvanitika Albanian has exceptionally two `primary`
    # orthographies, a font with support for either should include the language
    aat_latin = "A B C D E F G H I J K L M N O P Q R S T U V W X Y Z Á Ä Ç È É Ë Í Ï Ó Ö Ú Ü Ý a b c d e f g h i j k l m n o p q r s t u v w x y z á ä ç è é ë í ï ó ö ú ü ý"  # noqa
    aat = Language(Langs["aat"], "aat")
    support = aat.supported(aat_latin)
    assert ("Latin" in support.keys()) is True
    assert ("Greek" not in support.keys()) is True
    assert len(aat["orthographies"]) == 1


def test_language_combined_orthographies():
    Langs = Languages()

    # E.g. Serbian or Japanese have multiple orthographies that should be
    # treated as a combination, e.g. require all for support
    srp = Language(Langs["srp"], "srp")
    srp_cyrillic = 'А Б В Г Д Е Ж З И К Л М Н О П Р С Т У Ф Х Ц Ч Ш Ђ Ј Љ Њ Ћ Џ а б в г д е ж з и к л м н о п р с т у ф х ц ч ш ђ ј љ њ ћ џ ◌́'  # noqa
    srp_latin = 'A B C D E F G H I J K L M N O P Q R S T U V W X Y Z Ć Č Đ Ś Š Ź Ž a b c d e f g h i j k l m n o p q r s t u v w x y z ć č đ ś š ź ž'  # noqa

    # Checking support with just the one script will no list the language
    support = srp.supported(srp_latin)
    assert support == {}
    support = srp.supported(srp_cyrillic)
    assert support == {}

    # Checking with the combined chars this should now return both
    # orthographies
    srp = Language(Langs["srp"], "srp")
    combined = srp_cyrillic + " " + srp_latin
    support = srp.supported(combined)
    assert ("Cyrillic" in support) is True
    assert ("Latin" in support) is True
    assert ("srp" in support["Cyrillic"]) is True
    assert ("srp" in support["Latin"]) is True

    # Checking with --include-all-orthographies should return also a single
    # orthography
    srp = Language(Langs["srp"], "srp")
    support = srp.supported(srp_latin, checkAllOrthographies=True)
    assert ("Latin" in support) is True


def test_get_orthography():
    Langs = Languages()

    deu = Language(Langs["deu"], "deu")

    # By default and with not parameters it should return the primary
    # orthography
    deu_primary = deu.get_orthography()
    assert ("ẞ" in deu_primary["auxiliary"]) is True

    # Return a specific orthography
    deu_historical = deu.get_orthography(status="historical")
    assert deu_historical != deu_primary
    assert ("ẞ" not in deu_historical["auxiliary"]) is True

    # Raise error when a script does not exist
    with pytest.raises(KeyError):
        deu.get_orthography(script="Foobar")

    # Raise error when a status does not exist
    with pytest.raises(KeyError):
        deu.get_orthography(status="constructed")

    bos = Language(Langs["bos"], "bos")

    # Return a script specific orthography, even if that is not the primary one
    bos_cyrillic = bos.get_orthography("Cyrillic")
    assert ("Д" in bos_cyrillic["base"]) is True

    # However if for a specific script and status no orthography exists raise
    # exceptions
    with pytest.raises(KeyError):
        bos.get_orthography("Cyrillic", "primary")


def test_get_orthography_chars():
    Langs = Languages()

    deu = Language(Langs["deu"], "deu")
    orth = deu["orthographies"][0]

    deu_base_default = sorted(deu.get_orthography_chars(orth, "base",
                                                        decomposed=False))
    deu_base_decomposed = sorted(deu.get_orthography_chars(orth, "base",
                                                           decomposed=True))

    assert len(deu_base_default) > len(deu_base_decomposed)
    assert "Ä" in deu_base_default
    assert '̈' not in deu_base_default
    assert "Ä" not in deu_base_decomposed
    assert '̈' in deu_base_decomposed


def test_language_get_required_marks():
    Langs = Languages()

    deu = Language(Langs["deu"], "deu")
    orth = deu["orthographies"][0]
    """
    autonym: Deutsch
    auxiliary: À É ẞ à é
    base: A B C D E F G H I J K L M N O P Q R S T U V W X Y Z Ä Ö Ü a b c d e f g h i j k l m n o p q r s t u v w x y z ß ä ö ü
    marks: ◌̈ ◌̀ ◌́
    note: Includes capital Eszett as an auxiliary character for capitalization of ß.
    script: Latin
    status: primary
    """
    # Neither base nor aux has marks which cannot be derived form precomposed
    # chars, so there should not be any required marks
    assert deu.get_required_marks(orth, "base") == []
    assert deu.get_required_marks(orth, "aux") == []
    # Base only requires diesresis comb
    assert deu.get_all_marks(orth, "base") == ['̈']
    # Aux requires acute and grave comb, and also the base dieresis comb
    assert deu.get_all_marks(orth, "aux") == ['̈', '̀', '́']

