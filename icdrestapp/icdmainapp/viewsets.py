# from rest_framework import viewsets
# from . import models
# from . import serializers
# from .common.ResponseModelViewSet import ResponseModelViewSet

# class  ICDVersionViewset(ResponseModelViewSet):
#     queryset = models.ICDVersion.objects.all()
#     serializer_class = serializers.ICDVersionSerializer

    #list() retrive() create() update() destroy()

from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework.generics import ListAPIView
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from .models import ICDVersion
from .models import ICDCode
from .serializers import ICDVersionSerializer
from .serializers import ICDCodeSerializer

import csv
import re

@api_view(['GET', 'POST'])
def icdverion_list(request):
    response_format = {}
    """
    List all code snippets, or create a new snippet.
    """
    if request.method == 'GET':
        snippets = ICDVersion.objects.all()
        serializer = ICDVersionSerializer(snippets, many=True)
        response_format["status"] = 'success'
        response_format["data"] = serializer.data
        if not serializer.data:
            response_format["message"] = "List empty"
        return Response(response_format)

    elif request.method == 'POST':
        if ("version" in request.data):
            serializer = ICDVersionSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                response_format["status"] = 'success'
                response_format["data"] = serializer.data
                return Response(response_format, status=status.HTTP_201_CREATED)
            response_format["status"] = 'error'
            response_format["errors"] = serializer.errors
            return Response(response_format, status=status.HTTP_400_BAD_REQUEST)
        else:
            response_format["status"] = 'error'
            response_format["message"] = 'Version is required'
            return Response(response_format, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'DELETE'])
def icdverion_detail(request, pk):
    response_format = {}
    """
    Retrieve, update or delete a code snippet.
    """
    try:
        snippet = ICDVersion.objects.get(pk=pk)
    except ICDVersion.DoesNotExist:
        response_format["status"] = 'error'
        response_format["errors"] = 'Data Not found'
        return Response(response_format, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = ICDVersionSerializer(snippet)
        response_format["status"] = 'success'
        response_format["data"] = serializer.data
        return Response(response_format)

    elif request.method == 'DELETE':
        snippet.delete()
        response_format["status"] = 'success'
        response_format["message"] = 'Deleted Succesfully'
        return Response(response_format)



# FOR ICD CODE
@api_view(['GET', 'POST'])
def icdcode_list(request, av):
    response_format = {}

    try:
        snippet = ICDVersion.objects.get(version=av)
    except ICDVersion.DoesNotExist:
        response_format["status"] = 'error'
        response_format["errors"] = 'ICD Code Version Not found'
        return Response(response_format, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        # snippets = ICDCode.objects.filter(appVersion=av)

        snippets = ICDCode.objects.filter(appVersion=av).values().order_by('id') 

        page = request.GET.get('page')
        paginator = Paginator(snippets, 20)

        try:
            icdCodes = paginator.page(page)
        except PageNotAnInteger:
            icdCodes = paginator.page(1)
        except EmptyPage:
            icdCodes = paginator.page(paginator.num_pages)

        # serializer = ICDCodeSerializer(snippets, many=True)
        response_format["status"] = 'success'
        response_format["page"] = page or 1
        response_format["number_of_pages"] = paginator.num_pages
        response_format["data"] = list(icdCodes)
        if not icdCodes:
            response_format["message"] = "List empty"
        return Response(response_format)

    elif request.method == 'POST':
        if ("diagnosisCode" in request.data):
            diagnosisCode = request.data['diagnosisCode']
            try:
                snippet = ICDCode.objects.get(diagnosisCode=diagnosisCode, appVersion=av)
                response_format["status"] = 'error'
                response_format["errors"] = 'ICD Diagnoses code {dcode} available for ICD Version {appV}'.format(appV = av, dcode=diagnosisCode)
                return Response(response_format, status=status.HTTP_404_NOT_FOUND)
            except ICDCode.DoesNotExist:
                request.data["appVersion"] = av
                serializer = ICDCodeSerializer(data=request.data)
                if serializer.is_valid():
                    serializer.save()
                    response_format["status"] = 'success'
                    response_format["message"] = "Successfully added ICDCode"
                    response_format["data"] = serializer.data
                    return Response(response_format)
                response_format["status"] = 'error'
                response_format["errors"] = serializer.errors
                return Response(response_format, status=status.HTTP_400_BAD_REQUEST)
        else:
            response_format["status"] = 'error'
            response_format["message"] = 'Diagnoses code is required'
            return Response(response_format, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'DELETE', 'PUT'])
def icdcode_detail(request, av, pk):
    response_format = {}
    """
    Retrieve, update or delete a code snippet.
    """

    try:
        snippet = ICDVersion.objects.get(version=av)
    except ICDVersion.DoesNotExist:
        response_format["status"] = 'error'
        response_format["errors"] = 'ICD Code Version Not found'
        return Response(response_format, status=status.HTTP_404_NOT_FOUND)

    try:
        snippet = ICDCode.objects.get(pk=pk, appVersion=av)
    except ICDCode.DoesNotExist:
        response_format["status"] = 'error'
        response_format["errors"] = 'ICD Data Not found fro ICD Version {appV}'.format(appV = av)
        return Response(response_format, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = ICDCodeSerializer(snippet)
        response_format["status"] = 'success'
        response_format["data"] = serializer.data
        return Response(response_format)

    elif request.method == 'PUT':
        if ("diagnosisCode" in request.data):
            serializer = ICDCodeSerializer(snippet, data=request.data)
            if serializer.is_valid():
                serializer.save()
                response_format["status"] = 'success'
                response_format["message"] = "Successfully updated ICDCode"
                response_format["data"] = serializer.data
                return Response(response_format)
            response_format["status"] = 'error'
            response_format["errors"] = serializer.errors
            return Response(response_format, status=status.HTTP_400_BAD_REQUEST)
        else:
            response_format["status"] = 'error'
            response_format["message"] = 'Diagnoses code is required'
            return Response(response_format, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        snippet.delete()
        response_format["status"] = 'success'
        response_format["message"] = 'Deleted ICD Code Succesfully'
        return Response(response_format)


@api_view(['GET'])
def import_data(request):
    f = """A00,0,A000,"Cholera due to Vibrio cholerae 01, biovar cholerae","Cholera due to Vibrio cholerae 01, biovar cholerae",Cholera,9
A010,0,A0100,"Typhoid fever, unspecified","Typhoid fever, unspecified",Typhoid fever,9
A02,0,A020,Salmonella enteritis,Salmonella enteritis,Other salmonella infections,9
A022,0,A0220,"Localized salmonella infection, unspecified","Localized salmonella infection, unspecified",Localized salmonella infections,9
A03,0,A030,Shigellosis due to Shigella dysenteriae,Shigellosis due to Shigella dysenteriae,Shigellosis,9
A04,0,A040,Enteropathogenic Escherichia coli infection,Enteropathogenic Escherichia coli infection,Other bacterial intestinal infections,9
A05,0,A050,Foodborne staphylococcal intoxication,Foodborne staphylococcal intoxication,"Other bacterial foodborne intoxications, not elsewhere classified",9
A06,0,A060,Acute amebic dysentery,Acute amebic dysentery,Amebiasis,9
A07,0,A070,Balantidiasis,Balantidiasis,Other protozoal intestinal diseases,9
A08,0,A080,Rotaviral enteritis,Rotaviral enteritis,Viral and other specified intestinal infections,9
A15,0,A150,Tuberculosis of lung,Tuberculosis of lung,Respiratory tuberculosis,9
A17,0,A170,Tuberculous meningitis,Tuberculous meningitis,Tuberculosis of nervous system,9
A181,0,A1810,"Tuberculosis of genitourinary system, unspecified","Tuberculosis of genitourinary system, unspecified",Tuberculosis of genitourinary system,9
A185,0,A1850,"Tuberculosis of eye, unspecified","Tuberculosis of eye, unspecified",Tuberculosis of eye,9
A19,0,A190,Acute miliary tuberculosis of a single specified site,Acute miliary tuberculosis of a single specified site,Miliary tuberculosis,9
A20,0,A200,Bubonic plague,Bubonic plague,Plague,9
A21,0,A210,Ulceroglandular tularemia,Ulceroglandular tularemia,Tularemia,9
A22,0,A220,Cutaneous anthrax,Cutaneous anthrax,Anthrax,9
A23,0,A230,Brucellosis due to Brucella melitensis,Brucellosis due to Brucella melitensis,Brucellosis,9
A24,0,A240,Glanders,Glanders,Glanders and melioidosis,9
A25,0,A250,Spirillosis,Spirillosis,Rat-bite fevers,9
A26,0,A260,Cutaneous erysipeloid,Cutaneous erysipeloid,Erysipeloid,9
A27,0,A270,Leptospirosis icterohemorrhagica,Leptospirosis icterohemorrhagica,Leptospirosis,9
A28,0,A280,Pasteurellosis,Pasteurellosis,"Other zoonotic bacterial diseases, not elsewhere classified",9
A30,0,A300,Indeterminate leprosy,Indeterminate leprosy,Leprosy [Hansen's disease],9
A31,0,A310,Pulmonary mycobacterial infection,Pulmonary mycobacterial infection,Infection due to other mycobacteria,9
A32,0,A320,Cutaneous listeriosis,Cutaneous listeriosis,Listeriosis,9
A36,0,A360,Pharyngeal diphtheria,Pharyngeal diphtheria,Diphtheria,9
A370,0,A3700,Whooping cough due to Bordetella pertussis without pneumonia,Whooping cough due to Bordetella pertussis without pneumonia,Whooping cough due to Bordetella pertussis,9
A371,0,A3710,Whooping cough due to Bordetella parapertussis w/o pneumonia,Whooping cough due to Bordetella parapertussis without pneumonia,Whooping cough due to Bordetella parapertussis,9
A378,0,A3780,Whooping cough due to other Bordetella species w/o pneumonia,Whooping cough due to other Bordetella species without pneumonia,Whooping cough due to other Bordetella species,9
A379,0,A3790,"Whooping cough, unspecified species without pneumonia","Whooping cough, unspecified species without pneumonia","Whooping cough, unspecified species",9
A38,0,A380,Scarlet fever with otitis media,Scarlet fever with otitis media,Scarlet fever,9
A39,0,A390,Meningococcal meningitis,Meningococcal meningitis,Meningococcal infection,9
A395,0,A3950,"Meningococcal carditis, unspecified","Meningococcal carditis, unspecified",Meningococcal heart disease,9
A40,0,A400,"Sepsis due to streptococcus, group A","Sepsis due to streptococcus, group A",Streptococcal sepsis,9
A415,0,A4150,"Gram-negative sepsis, unspecified","Gram-negative sepsis, unspecified",Sepsis due to other Gram-negative organisms,9
A42,0,A420,Pulmonary actinomycosis,Pulmonary actinomycosis,Actinomycosis,9
A43,0,A430,Pulmonary nocardiosis,Pulmonary nocardiosis,Nocardiosis,9
A44,0,A440,Systemic bartonellosis,Systemic bartonellosis,Bartonellosis,9
A48,0,A480,Gas gangrene,Gas gangrene,"Other bacterial diseases, not elsewhere classified",9
A503,0,A5030,"Late congenital syphilitic oculopathy, unspecified","Late congenital syphilitic oculopathy, unspecified",Late congenital syphilitic oculopathy,9
A504,0,A5040,"Late congenital neurosyphilis, unspecified","Late congenital neurosyphilis, unspecified",Late congenital neurosyphilis [juvenile neurosyphilis],9
A51,0,A510,Primary genital syphilis,Primary genital syphilis,Early syphilis,9
A520,0,A5200,"Cardiovascular syphilis, unspecified","Cardiovascular syphilis, unspecified",Cardiovascular and cerebrovascular syphilis,9
A521,0,A5210,"Symptomatic neurosyphilis, unspecified","Symptomatic neurosyphilis, unspecified",Symptomatic neurosyphilis,9
A53,0,A530,"Latent syphilis, unspecified as early or late","Latent syphilis, unspecified as early or late",Other and unspecified syphilis,9
A540,0,A5400,"Gonococcal infection of lower genitourinary tract, unsp","Gonococcal infection of lower genitourinary tract, unspecified",Gonococcal infection of lower genitourinary tract without periurethral or accessory gland abscess,9
A543,0,A5430,"Gonococcal infection of eye, unspecified","Gonococcal infection of eye, unspecified",Gonococcal infection of eye,9
A544,0,A5440,"Gonococcal infection of musculoskeletal system, unspecified","Gonococcal infection of musculoskeletal system, unspecified",Gonococcal infection of musculoskeletal system,9
A560,0,A5600,"Chlamydial infection of lower genitourinary tract, unsp","Chlamydial infection of lower genitourinary tract, unspecified",Chlamydial infection of lower genitourinary tract,9
A590,0,A5900,"Urogenital trichomoniasis, unspecified","Urogenital trichomoniasis, unspecified",Urogenital trichomoniasis,9
A600,0,A6000,"Herpesviral infection of urogenital system, unspecified","Herpesviral infection of urogenital system, unspecified",Herpesviral infection of genitalia and urogenital tract,9
B33,0,B330,Epidemic myalgia,Epidemic myalgia,"Other viral diseases, not elsewhere classified",9
A63,0,A630,Anogenital (venereal) warts,Anogenital (venereal) warts,"Other predominantly sexually transmitted diseases, not elsewhere classified",9
A66,0,A660,Initial lesions of yaws,Initial lesions of yaws,Yaws,9
A67,0,A670,Primary lesions of pinta,Primary lesions of pinta,Pinta [carate],9
A68,0,A680,Louse-borne relapsing fever,Louse-borne relapsing fever,Relapsing fevers,9
A69,0,A690,Necrotizing ulcerative stomatitis,Necrotizing ulcerative stomatitis,Other spirochetal infections,9
A692,0,A6920,"Lyme disease, unspecified","Lyme disease, unspecified",Lyme disease,9
A71,0,A710,Initial stage of trachoma,Initial stage of trachoma,Trachoma,9
A74,0,A740,Chlamydial conjunctivitis,Chlamydial conjunctivitis,Other diseases caused by chlamydiae,9
A75,0,A750,Epidemic louse-borne typhus fever d/t Rickettsia prowazekii,Epidemic louse-borne typhus fever due to Rickettsia prowazekii,Typhus fever,9
A77,0,A770,Spotted fever due to Rickettsia rickettsii,Spotted fever due to Rickettsia rickettsii,Spotted fever [tick-borne rickettsioses],9
A774,0,A7740,"Ehrlichiosis, unspecified","Ehrlichiosis, unspecified",Ehrlichiosis,9
A79,0,A790,Trench fever,Trench fever,Other rickettsioses,9
A80,0,A800,"Acute paralytic poliomyelitis, vaccine-associated","Acute paralytic poliomyelitis, vaccine-associated",Acute poliomyelitis,9
A803,0,A8030,"Acute paralytic poliomyelitis, unspecified","Acute paralytic poliomyelitis, unspecified","Acute paralytic poliomyelitis, other and unspecified",9
A810,0,A8100,"Creutzfeldt-Jakob disease, unspecified","Creutzfeldt-Jakob disease, unspecified",Creutzfeldt-Jakob disease,9
A82,0,A820,Sylvatic rabies,Sylvatic rabies,Rabies,9
A83,0,A830,Japanese encephalitis,Japanese encephalitis,Mosquito-borne viral encephalitis,9
A84,0,A840,Far Eastern tick-borne encephalitis,Far Eastern tick-borne encephalitis [Russian spring-summer encephalitis],Tick-borne viral encephalitis,9
A85,0,A850,Enteroviral encephalitis,Enteroviral encephalitis,"Other viral encephalitis, not elsewhere classified",9
A87,0,A870,Enteroviral meningitis,Enteroviral meningitis,Viral meningitis,9
A88,0,A880,Enteroviral exanthematous fever [Boston exanthem],Enteroviral exanthematous fever [Boston exanthem],"Other viral infections of central nervous system, not elsewhere classified",9
A92,0,A920,Chikungunya virus disease,Chikungunya virus disease,Other mosquito-borne viral fevers,9
A923,0,A9230,"West Nile virus infection, unspecified","West Nile virus infection, unspecified",West Nile virus infection,9
A93,0,A930,Oropouche virus disease,Oropouche virus disease,"Other arthropod-borne viral fevers, not elsewhere classified",9
A95,0,A950,Sylvatic yellow fever,Sylvatic yellow fever,Yellow fever,9
A96,0,A960,Junin hemorrhagic fever,Junin hemorrhagic fever,Arenaviral hemorrhagic fever,9
A98,0,A980,Crimean-Congo hemorrhagic fever,Crimean-Congo hemorrhagic fever,"Other viral hemorrhagic fevers, not elsewhere classified",9
B00,0,B000,Eczema herpeticum,Eczema herpeticum,Herpesviral [herpes simplex] infections,9
B005,0,B0050,"Herpesviral ocular disease, unspecified","Herpesviral ocular disease, unspecified",Herpesviral ocular disease,9
B01,0,B010,Varicella meningitis,Varicella meningitis,Varicella [chickenpox],9
B02,0,B020,Zoster encephalitis,Zoster encephalitis,Zoster [herpes zoster],9
B023,0,B0230,"Zoster ocular disease, unspecified","Zoster ocular disease, unspecified",Zoster ocular disease,9
B05,0,B050,Measles complicated by encephalitis,Measles complicated by encephalitis,Measles,9
B060,0,B0600,"Rubella with neurological complication, unspecified","Rubella with neurological complication, unspecified",Rubella with neurological complications,9
B07,0,B070,Plantar wart,Plantar wart,Viral warts,9
B0801,0,B08010,Cowpox,Cowpox,Cowpox and vaccinia not from vaccine,9
B082,0,B0820,"Exanthema subitum [sixth disease], unspecified","Exanthema subitum [sixth disease], unspecified",Exanthema subitum [sixth disease],9
B086,0,B0860,"Parapoxvirus infection, unspecified","Parapoxvirus infection, unspecified",Parapoxvirus infections,9
B087,0,B0870,"Yatapoxvirus infection, unspecified","Yatapoxvirus infection, unspecified",Yatapoxvirus infections,9
B15,0,B150,Hepatitis A with hepatic coma,Hepatitis A with hepatic coma,Acute hepatitis A,9
B16,0,B160,Acute hepatitis B with delta-agent with hepatic coma,Acute hepatitis B with delta-agent with hepatic coma,Acute hepatitis B,9
B17,0,B170,Acute delta-(super) infection of hepatitis B carrier,Acute delta-(super) infection of hepatitis B carrier,Other acute viral hepatitis,9
B171,0,B1710,Acute hepatitis C without hepatic coma,Acute hepatitis C without hepatic coma,Acute hepatitis C,9
B18,0,B180,Chronic viral hepatitis B with delta-agent,Chronic viral hepatitis B with delta-agent,Chronic viral hepatitis,9
B19,0,B190,Unspecified viral hepatitis with hepatic coma,Unspecified viral hepatitis with hepatic coma,Unspecified viral hepatitis,9
B191,0,B1910,Unspecified viral hepatitis B without hepatic coma,Unspecified viral hepatitis B without hepatic coma,Unspecified viral hepatitis B,9
B192,0,B1920,Unspecified viral hepatitis C without hepatic coma,Unspecified viral hepatitis C without hepatic coma,Unspecified viral hepatitis C,9
B25,0,B250,Cytomegaloviral pneumonitis,Cytomegaloviral pneumonitis,Cytomegaloviral disease,9
B26,0,B260,Mumps orchitis,Mumps orchitis,Mumps,9
B270,0,B2700,Gammaherpesviral mononucleosis without complication,Gammaherpesviral mononucleosis without complication,Gammaherpesviral mononucleosis,9
B271,0,B2710,Cytomegaloviral mononucleosis without complications,Cytomegaloviral mononucleosis without complications,Cytomegaloviral mononucleosis,9
B278,0,B2780,Other infectious mononucleosis without complication,Other infectious mononucleosis without complication,Other infectious mononucleosis,9
B279,0,B2790,"Infectious mononucleosis, unspecified without complication","Infectious mononucleosis, unspecified without complication","Infectious mononucleosis, unspecified",9
B30,0,B300,Keratoconjunctivitis due to adenovirus,Keratoconjunctivitis due to adenovirus,Viral conjunctivitis,9
A96,2,A962,Lassa fever,Lassa fever,Arenaviral hemorrhagic fever,9
B332,0,B3320,"Viral carditis, unspecified","Viral carditis, unspecified",Viral carditis,9
B34,0,B340,"Adenovirus infection, unspecified","Adenovirus infection, unspecified",Viral infection of unspecified site,9
B35,0,B350,Tinea barbae and tinea capitis,Tinea barbae and tinea capitis,Dermatophytosis,9
B36,0,B360,Pityriasis versicolor,Pityriasis versicolor,Other superficial mycoses,9
B37,0,B370,Candidal stomatitis,Candidal stomatitis,Candidiasis,9
B38,0,B380,Acute pulmonary coccidioidomycosis,Acute pulmonary coccidioidomycosis,Coccidioidomycosis,9
B39,0,B390,Acute pulmonary histoplasmosis capsulati,Acute pulmonary histoplasmosis capsulati,Histoplasmosis,9
B40,0,B400,Acute pulmonary blastomycosis,Acute pulmonary blastomycosis,Blastomycosis,9
B41,0,B410,Pulmonary paracoccidioidomycosis,Pulmonary paracoccidioidomycosis,Paracoccidioidomycosis,9
B42,0,B420,Pulmonary sporotrichosis,Pulmonary sporotrichosis,Sporotrichosis,9
B43,0,B430,Cutaneous chromomycosis,Cutaneous chromomycosis,Chromomycosis and pheomycotic abscess,9
B44,0,B440,Invasive pulmonary aspergillosis,Invasive pulmonary aspergillosis,Aspergillosis,9
B45,0,B450,Pulmonary cryptococcosis,Pulmonary cryptococcosis,Cryptococcosis,9
B46,0,B460,Pulmonary mucormycosis,Pulmonary mucormycosis,Zygomycosis,9
B47,0,B470,Eumycetoma,Eumycetoma,Mycetoma,9
B48,0,B480,Lobomycosis,Lobomycosis,"Other mycoses, not elsewhere classified",9
B50,0,B500,Plasmodium falciparum malaria with cerebral complications,Plasmodium falciparum malaria with cerebral complications,Plasmodium falciparum malaria,9
B51,0,B510,Plasmodium vivax malaria with rupture of spleen,Plasmodium vivax malaria with rupture of spleen,Plasmodium vivax malaria,9
B52,0,B520,Plasmodium malariae malaria with nephropathy,Plasmodium malariae malaria with nephropathy,Plasmodium malariae malaria,9
B53,0,B530,Plasmodium ovale malaria,Plasmodium ovale malaria,Other specified malaria,9
B55,0,B550,Visceral leishmaniasis,Visceral leishmaniasis,Leishmaniasis,9
B56,0,B560,Gambiense trypanosomiasis,Gambiense trypanosomiasis,African trypanosomiasis,9
B57,0,B570,Acute Chagas' disease with heart involvement,Acute Chagas' disease with heart involvement,Chagas' disease,9
B573,0,B5730,"Chagas'' disease with digestive system involvement, unsp","Chagas'' disease with digestive system involvement, unspecified",Chagas' disease (chronic) with digestive system involvement,9
B574,0,B5740,"Chagas'' disease with nervous system involvement, unspecified","Chagas'' disease with nervous system involvement, unspecified",Chagas' disease (chronic) with nervous system involvement,9
B580,0,B5800,"Toxoplasma oculopathy, unspecified","Toxoplasma oculopathy, unspecified",Toxoplasma oculopathy,9
B60,0,B600,Babesiosis,Babesiosis,"Other protozoal diseases, not elsewhere classified",9
B601,0,B6010,"Acanthamebiasis, unspecified","Acanthamebiasis, unspecified",Acanthamebiasis,9
B65,0,B650,Schistosomiasis due to Schistosoma haematobium,Schistosomiasis due to Schistosoma haematobium [urinary schistosomiasis],Schistosomiasis [bilharziasis],9
B66,0,B660,Opisthorchiasis,Opisthorchiasis,Other fluke infections,9
B67,0,B670,Echinococcus granulosus infection of liver,Echinococcus granulosus infection of liver,Echinococcosis,9
B679,0,B6790,"Echinococcosis, unspecified","Echinococcosis, unspecified","Echinococcosis, other and unspecified",9
B68,0,B680,Taenia solium taeniasis,Taenia solium taeniasis,Taeniasis,9
B69,0,B690,Cysticercosis of central nervous system,Cysticercosis of central nervous system,Cysticercosis,9
B70,0,B700,Diphyllobothriasis,Diphyllobothriasis,Diphyllobothriasis and sparganosis,9
B71,0,B710,Hymenolepiasis,Hymenolepiasis,Other cestode infections,9
B730,0,B7300,"Onchocerciasis with eye involvement, unspecified","Onchocerciasis with eye involvement, unspecified",Onchocerciasis with eye disease,9
B74,0,B740,Filariasis due to Wuchereria bancrofti,Filariasis due to Wuchereria bancrofti,Filariasis,9
B76,0,B760,Ancylostomiasis,Ancylostomiasis,Hookworm diseases,9
B77,0,B770,Ascariasis with intestinal complications,Ascariasis with intestinal complications,Ascariasis,9
B78,0,B780,Intestinal strongyloidiasis,Intestinal strongyloidiasis,Strongyloidiasis,9
B81,0,B810,Anisakiasis,Anisakiasis,"Other intestinal helminthiases, not elsewhere classified",9
B82,0,B820,"Intestinal helminthiasis, unspecified","Intestinal helminthiasis, unspecified",Unspecified intestinal parasitism,9
B83,0,B830,Visceral larva migrans,Visceral larva migrans,Other helminthiases,9
B85,0,B850,Pediculosis due to Pediculus humanus capitis,Pediculosis due to Pediculus humanus capitis,Pediculosis and phthiriasis,9
B87,0,B870,Cutaneous myiasis,Cutaneous myiasis,Myiasis,9
B88,0,B880,Other acariasis,Other acariasis,Other infestations,9
B90,0,B900,Sequelae of central nervous system tuberculosis,Sequelae of central nervous system tuberculosis,Sequelae of tuberculosis,9
B94,0,B940,Sequelae of trachoma,Sequelae of trachoma,Sequelae of other and unspecified infectious and parasitic diseases,9
B95,0,B950,"Streptococcus, group A, causing diseases classd elswhr","Streptococcus, group A, as the cause of diseases classified elsewhere","Streptococcus, Staphylococcus, and Enterococcus as the cause of diseases classified elsewhere",9
B96,0,B960,Mycoplasma pneumoniae as the cause of diseases classd elswhr,Mycoplasma pneumoniae [M. pneumoniae] as the cause of diseases classified elsewhere,Other bacterial agents as the cause of diseases classified elsewhere,9
B962,0,B9620,Unsp Escherichia coli as the cause of diseases classd elswhr,Unspecified Escherichia coli [E. coli] as the cause of diseases classified elsewhere,Escherichia coli [E. coli ] as the cause of diseases classified elsewhere,9
B97,0,B970,Adenovirus as the cause of diseases classified elsewhere,Adenovirus as the cause of diseases classified elsewhere,Viral agents as the cause of diseases classified elsewhere,9
B971,0,B9710,Unsp enterovirus as the cause of diseases classd elswhr,Unspecified enterovirus as the cause of diseases classified elsewhere,Enterovirus as the cause of diseases classified elsewhere,9
B973,0,B9730,Unsp retrovirus as the cause of diseases classd elswhr,Unspecified retrovirus as the cause of diseases classified elsewhere,Retrovirus as the cause of diseases classified elsewhere,9
C00,0,C000,Malignant neoplasm of external upper lip,Malignant neoplasm of external upper lip,Malignant neoplasm of lip,9
C02,0,C020,Malignant neoplasm of dorsal surface of tongue,Malignant neoplasm of dorsal surface of tongue,Malignant neoplasm of other and unspecified parts of tongue,9
C03,0,C030,Malignant neoplasm of upper gum,Malignant neoplasm of upper gum,Malignant neoplasm of gum,9
C04,0,C040,Malignant neoplasm of anterior floor of mouth,Malignant neoplasm of anterior floor of mouth,Malignant neoplasm of floor of mouth,9
C05,0,C050,Malignant neoplasm of hard palate,Malignant neoplasm of hard palate,Malignant neoplasm of palate,9
C06,0,C060,Malignant neoplasm of cheek mucosa,Malignant neoplasm of cheek mucosa,Malignant neoplasm of other and unspecified parts of mouth,9
C068,0,C0680,Malignant neoplasm of ovrlp sites of unsp parts of mouth,Malignant neoplasm of overlapping sites of unspecified parts of mouth,Malignant neoplasm of overlapping sites of other and unspecified parts of mouth,9
C08,0,C080,Malignant neoplasm of submandibular gland,Malignant neoplasm of submandibular gland,Malignant neoplasm of other and unspecified major salivary glands,9
C09,0,C090,Malignant neoplasm of tonsillar fossa,Malignant neoplasm of tonsillar fossa,Malignant neoplasm of tonsil,9
C10,0,C100,Malignant neoplasm of vallecula,Malignant neoplasm of vallecula,Malignant neoplasm of oropharynx,9
C11,0,C110,Malignant neoplasm of superior wall of nasopharynx,Malignant neoplasm of superior wall of nasopharynx,Malignant neoplasm of nasopharynx,9
C13,0,C130,Malignant neoplasm of postcricoid region,Malignant neoplasm of postcricoid region,Malignant neoplasm of hypopharynx,9
C14,0,C140,"Malignant neoplasm of pharynx, unspecified","Malignant neoplasm of pharynx, unspecified","Malignant neoplasm of other and ill-defined sites in the lip, oral cavity and pharynx",9
C16,0,C160,Malignant neoplasm of cardia,Malignant neoplasm of cardia,Malignant neoplasm of stomach,9
C17,0,C170,Malignant neoplasm of duodenum,Malignant neoplasm of duodenum,Malignant neoplasm of small intestine,9
C18,0,C180,Malignant neoplasm of cecum,Malignant neoplasm of cecum,Malignant neoplasm of colon,9
C21,0,C210,"Malignant neoplasm of anus, unspecified","Malignant neoplasm of anus, unspecified",Malignant neoplasm of anus and anal canal,9
C22,0,C220,Liver cell carcinoma,Liver cell carcinoma,Malignant neoplasm of liver and intrahepatic bile ducts,9
C24,0,C240,Malignant neoplasm of extrahepatic bile duct,Malignant neoplasm of extrahepatic bile duct,Malignant neoplasm of other and unspecified parts of biliary tract,9
C25,0,C250,Malignant neoplasm of head of pancreas,Malignant neoplasm of head of pancreas,Malignant neoplasm of pancreas,9
C26,0,C260,"Malignant neoplasm of intestinal tract, part unspecified","Malignant neoplasm of intestinal tract, part unspecified",Malignant neoplasm of other and ill-defined digestive organs,9
C30,0,C300,Malignant neoplasm of nasal cavity,Malignant neoplasm of nasal cavity,Malignant neoplasm of nasal cavity and middle ear,9
C31,0,C310,Malignant neoplasm of maxillary sinus,Malignant neoplasm of maxillary sinus,Malignant neoplasm of accessory sinuses,9
C32,0,C320,Malignant neoplasm of glottis,Malignant neoplasm of glottis,Malignant neoplasm of larynx,9
C340,0,C3400,Malignant neoplasm of unspecified main bronchus,Malignant neoplasm of unspecified main bronchus,Malignant neoplasm of main bronchus,9
C341,0,C3410,"Malignant neoplasm of upper lobe, unsp bronchus or lung","Malignant neoplasm of upper lobe, unspecified bronchus or lung","Malignant neoplasm of upper lobe, bronchus or lung",9
C343,0,C3430,"Malignant neoplasm of lower lobe, unsp bronchus or lung","Malignant neoplasm of lower lobe, unspecified bronchus or lung","Malignant neoplasm of lower lobe, bronchus or lung",9
C348,0,C3480,Malignant neoplasm of ovrlp sites of unsp bronchus and lung,Malignant neoplasm of overlapping sites of unspecified bronchus and lung,Malignant neoplasm of overlapping sites of bronchus and lung,9
C349,0,C3490,Malignant neoplasm of unsp part of unsp bronchus or lung,Malignant neoplasm of unspecified part of unspecified bronchus or lung,Malignant neoplasm of unspecified part of bronchus or lung,9
C38,0,C380,Malignant neoplasm of heart,Malignant neoplasm of heart,"Malignant neoplasm of heart, mediastinum and pleura",9
C39,0,C390,"Malignant neoplasm of upper respiratory tract, part unsp","Malignant neoplasm of upper respiratory tract, part unspecified",Malignant neoplasm of other and ill-defined sites in the respiratory system and intrathoracic organs,9
C400,0,C4000,Malig neoplasm of scapula and long bones of unsp upper limb,Malignant neoplasm of scapula and long bones of unspecified upper limb,Malignant neoplasm of scapula and long bones of upper limb,9
C401,0,C4010,Malignant neoplasm of short bones of unspecified upper limb,Malignant neoplasm of short bones of unspecified upper limb,Malignant neoplasm of short bones of upper limb,9
C402,0,C4020,Malignant neoplasm of long bones of unspecified lower limb,Malignant neoplasm of long bones of unspecified lower limb,Malignant neoplasm of long bones of lower limb,9
C403,0,C4030,Malignant neoplasm of short bones of unspecified lower limb,Malignant neoplasm of short bones of unspecified lower limb,Malignant neoplasm of short bones of lower limb,9
C408,0,C4080,Malig neoplm of ovrlp sites of bone/artic cartl of unsp limb,Malignant neoplasm of overlapping sites of bone and articular cartilage of unspecified limb,Malignant neoplasm of overlapping sites of bone and articular cartilage of limb,9
C409,0,C4090,Malig neoplasm of unsp bones and artic cartlg of unsp limb,Malignant neoplasm of unspecified bones and articular cartilage of unspecified limb,Malignant neoplasm of unspecified bones and articular cartilage of limb,9
C41,0,C410,Malignant neoplasm of bones of skull and face,Malignant neoplasm of bones of skull and face,Malignant neoplasm of bone and articular cartilage of other and unspecified sites,9
C43,0,C430,Malignant melanoma of lip,Malignant melanoma of lip,Malignant melanoma of skin,9
C431,0,C4310,"Malignant melanoma of unspecified eyelid, including canthus","Malignant melanoma of unspecified eyelid, including canthus","Malignant melanoma of eyelid, including canthus",9
C60,0,C600,Malignant neoplasm of prepuce,Malignant neoplasm of prepuce,Malignant neoplasm of penis,9
C432,0,C4320,Malignant melanoma of unsp ear and external auricular canal,Malignant melanoma of unspecified ear and external auricular canal,Malignant melanoma of ear and external auricular canal,9
C433,0,C4330,Malignant melanoma of unspecified part of face,Malignant melanoma of unspecified part of face,Malignant melanoma of other and unspecified parts of face,9
C436,0,C4360,"Malignant melanoma of unsp upper limb, including shoulder","Malignant melanoma of unspecified upper limb, including shoulder","Malignant melanoma of upper limb, including shoulder",9
C437,0,C4370,"Malignant melanoma of unspecified lower limb, including hip","Malignant melanoma of unspecified lower limb, including hip","Malignant melanoma of lower limb, including hip",9
C4A,0,C4A0,Merkel cell carcinoma of lip,Merkel cell carcinoma of lip,Merkel cell carcinoma,9
C4A1,0,C4A10,"Merkel cell carcinoma of unsp eyelid, including canthus","Merkel cell carcinoma of unspecified eyelid, including canthus","Merkel cell carcinoma of eyelid, including canthus",9
C4A2,0,C4A20,Merkel cell carcinoma of unsp ear and external auric canal,Merkel cell carcinoma of unspecified ear and external auricular canal,Merkel cell carcinoma of ear and external auricular canal,9
C4A3,0,C4A30,Merkel cell carcinoma of unspecified part of face,Merkel cell carcinoma of unspecified part of face,Merkel cell carcinoma of other and unspecified parts of face,9
C4A6,0,C4A60,"Merkel cell carcinoma of unsp upper limb, including shoulder","Merkel cell carcinoma of unspecified upper limb, including shoulder","Merkel cell carcinoma of upper limb, including shoulder",9
C4A7,0,C4A70,"Merkel cell carcinoma of unsp lower limb, including hip","Merkel cell carcinoma of unspecified lower limb, including hip","Merkel cell carcinoma of lower limb, including hip",9
C440,0,C4400,Unspecified malignant neoplasm of skin of lip,Unspecified malignant neoplasm of skin of lip,Other and unspecified malignant neoplasm of skin of lip,9
C4430,0,C44300,Unsp malignant neoplasm of skin of unspecified part of face,Unspecified malignant neoplasm of skin of unspecified part of face,Unspecified malignant neoplasm of skin of other and unspecified parts of face,9
C4431,0,C44310,Basal cell carcinoma of skin of unspecified parts of face,Basal cell carcinoma of skin of unspecified parts of face,Basal cell carcinoma of skin of other and unspecified parts of face,9
C4432,0,C44320,Squamous cell carcinoma of skin of unspecified parts of face,Squamous cell carcinoma of skin of unspecified parts of face,Squamous cell carcinoma of skin of other and unspecified parts of face,9
C4439,0,C44390,Oth malignant neoplasm of skin of unspecified parts of face,Other specified malignant neoplasm of skin of unspecified parts of face,Other specified malignant neoplasm of skin of other and unspecified parts of face,9
C444,0,C4440,Unspecified malignant neoplasm of skin of scalp and neck,Unspecified malignant neoplasm of skin of scalp and neck,Other and unspecified malignant neoplasm of skin of scalp and neck,9
C4450,0,C44500,Unspecified malignant neoplasm of anal skin,Unspecified malignant neoplasm of anal skin,Unspecified malignant neoplasm of skin of trunk,9
C4451,0,C44510,Basal cell carcinoma of anal skin,Basal cell carcinoma of anal skin,Basal cell carcinoma of skin of trunk,9
C4452,0,C44520,Squamous cell carcinoma of anal skin,Squamous cell carcinoma of anal skin,Squamous cell carcinoma of skin of trunk,9
C4459,0,C44590,Other specified malignant neoplasm of anal skin,Other specified malignant neoplasm of anal skin,Other specified malignant neoplasm of skin of trunk,9
C448,0,C4480,Unspecified malignant neoplasm of overlapping sites of skin,Unspecified malignant neoplasm of overlapping sites of skin,Other and unspecified malignant neoplasm of overlapping sites of skin,9
C449,0,C4490,"Unspecified malignant neoplasm of skin, unspecified","Unspecified malignant neoplasm of skin, unspecified","Other and unspecified malignant neoplasm of skin, unspecified",9
C45,0,C450,Mesothelioma of pleura,Mesothelioma of pleura,Mesothelioma,9
C46,0,C460,Kaposi's sarcoma of skin,Kaposi's sarcoma of skin,Kaposi's sarcoma,9
C465,0,C4650,Kaposi's sarcoma of unspecified lung,Kaposi's sarcoma of unspecified lung,Kaposi's sarcoma of lung,9
C47,0,C470,"Malignant neoplasm of prph nerves of head, face and neck","Malignant neoplasm of peripheral nerves of head, face and neck",Malignant neoplasm of peripheral nerves and autonomic nervous system,9
C471,0,C4710,"Malig neoplm of prph nerves of unsp upper limb, inc shoulder","Malignant neoplasm of peripheral nerves of unspecified upper limb, including shoulder","Malignant neoplasm of peripheral nerves of upper limb, including shoulder",9
C472,0,C4720,"Malig neoplasm of prph nerves of unsp lower limb, inc hip","Malignant neoplasm of peripheral nerves of unspecified lower limb, including hip","Malignant neoplasm of peripheral nerves of lower limb, including hip",9
C48,0,C480,Malignant neoplasm of retroperitoneum,Malignant neoplasm of retroperitoneum,Malignant neoplasm of retroperitoneum and peritoneum,9
C49,0,C490,"Malig neoplm of conn and soft tissue of head, face and neck","Malignant neoplasm of connective and soft tissue of head, face and neck",Malignant neoplasm of other connective and soft tissue,9
C491,0,C4910,"Malig neoplm of conn & soft tiss of unsp upr lmb, inc shldr","Malignant neoplasm of connective and soft tissue of unspecified upper limb, including shoulder","Malignant neoplasm of connective and soft tissue of upper limb, including shoulder",9
C492,0,C4920,"Malig neoplm of conn and soft tiss of unsp low limb, inc hip","Malignant neoplasm of connective and soft tissue of unspecified lower limb, including hip","Malignant neoplasm of connective and soft tissue of lower limb, including hip",9
C49A,0,C49A0,"Gastrointestinal stromal tumor, unspecified site","Gastrointestinal stromal tumor, unspecified site",Gastrointestinal stromal tumor,9
C51,0,C510,Malignant neoplasm of labium majus,Malignant neoplasm of labium majus,Malignant neoplasm of vulva,9
C53,0,C530,Malignant neoplasm of endocervix,Malignant neoplasm of endocervix,Malignant neoplasm of cervix uteri,9
C54,0,C540,Malignant neoplasm of isthmus uteri,Malignant neoplasm of isthmus uteri,Malignant neoplasm of corpus uteri,9
C570,0,C5700,Malignant neoplasm of unspecified fallopian tube,Malignant neoplasm of unspecified fallopian tube,Malignant neoplasm of fallopian tube,9
C571,0,C5710,Malignant neoplasm of unspecified broad ligament,Malignant neoplasm of unspecified broad ligament,Malignant neoplasm of broad ligament,9
C572,0,C5720,Malignant neoplasm of unspecified round ligament,Malignant neoplasm of unspecified round ligament,Malignant neoplasm of round ligament,9
C620,0,C6200,Malignant neoplasm of unspecified undescended testis,Malignant neoplasm of unspecified undescended testis,Malignant neoplasm of undescended testis,9
C621,0,C6210,Malignant neoplasm of unspecified descended testis,Malignant neoplasm of unspecified descended testis,Malignant neoplasm of descended testis,9
C629,0,C6290,"Malig neoplasm of unsp testis, unsp descended or undescended","Malignant neoplasm of unspecified testis, unspecified whether descended or undescended","Malignant neoplasm of testis, unspecified whether descended or undescended",9
C630,0,C6300,Malignant neoplasm of unspecified epididymis,Malignant neoplasm of unspecified epididymis,Malignant neoplasm of epididymis,9
C631,0,C6310,Malignant neoplasm of unspecified spermatic cord,Malignant neoplasm of unspecified spermatic cord,Malignant neoplasm of spermatic cord,9
C67,0,C670,Malignant neoplasm of trigone of bladder,Malignant neoplasm of trigone of bladder,Malignant neoplasm of bladder,9
C68,0,C680,Malignant neoplasm of urethra,Malignant neoplasm of urethra,Malignant neoplasm of other and unspecified urinary organs,9
C690,0,C6900,Malignant neoplasm of unspecified conjunctiva,Malignant neoplasm of unspecified conjunctiva,Malignant neoplasm of conjunctiva,9
C691,0,C6910,Malignant neoplasm of unspecified cornea,Malignant neoplasm of unspecified cornea,Malignant neoplasm of cornea,9
C692,0,C6920,Malignant neoplasm of unspecified retina,Malignant neoplasm of unspecified retina,Malignant neoplasm of retina,9
C693,0,C6930,Malignant neoplasm of unspecified choroid,Malignant neoplasm of unspecified choroid,Malignant neoplasm of choroid,9
C694,0,C6940,Malignant neoplasm of unspecified ciliary body,Malignant neoplasm of unspecified ciliary body,Malignant neoplasm of ciliary body,9
C695,0,C6950,Malignant neoplasm of unspecified lacrimal gland and duct,Malignant neoplasm of unspecified lacrimal gland and duct,Malignant neoplasm of lacrimal gland and duct,9
C696,0,C6960,Malignant neoplasm of unspecified orbit,Malignant neoplasm of unspecified orbit,Malignant neoplasm of orbit,9
C698,0,C6980,Malignant neoplasm of ovrlp sites of unsp eye and adnexa,Malignant neoplasm of overlapping sites of unspecified eye and adnexa,Malignant neoplasm of overlapping sites of eye and adnexa,9
C699,0,C6990,Malignant neoplasm of unspecified site of unspecified eye,Malignant neoplasm of unspecified site of unspecified eye,Malignant neoplasm of unspecified site of eye,9
C70,0,C700,Malignant neoplasm of cerebral meninges,Malignant neoplasm of cerebral meninges,Malignant neoplasm of meninges,9
C71,0,C710,"Malignant neoplasm of cerebrum, except lobes and ventricles","Malignant neoplasm of cerebrum, except lobes and ventricles",Malignant neoplasm of brain,9
C72,0,C720,Malignant neoplasm of spinal cord,Malignant neoplasm of spinal cord,"Malignant neoplasm of spinal cord, cranial nerves and other parts of central nervous system",9
C722,0,C7220,Malignant neoplasm of unspecified olfactory nerve,Malignant neoplasm of unspecified olfactory nerve,Malignant neoplasm of olfactory nerve,9
C723,0,C7230,Malignant neoplasm of unspecified optic nerve,Malignant neoplasm of unspecified optic nerve,Malignant neoplasm of optic nerve,9
C724,0,C7240,Malignant neoplasm of unspecified acoustic nerve,Malignant neoplasm of unspecified acoustic nerve,Malignant neoplasm of acoustic nerve,9
C725,0,C7250,Malignant neoplasm of unspecified cranial nerve,Malignant neoplasm of unspecified cranial nerve,Malignant neoplasm of other and unspecified cranial nerves,9
C740,0,C7400,Malignant neoplasm of cortex of unspecified adrenal gland,Malignant neoplasm of cortex of unspecified adrenal gland,Malignant neoplasm of cortex of adrenal gland,9
C741,0,C7410,Malignant neoplasm of medulla of unspecified adrenal gland,Malignant neoplasm of medulla of unspecified adrenal gland,Malignant neoplasm of medulla of adrenal gland,9
C749,0,C7490,Malignant neoplasm of unsp part of unspecified adrenal gland,Malignant neoplasm of unspecified part of unspecified adrenal gland,Malignant neoplasm of unspecified part of adrenal gland,9
C75,0,C750,Malignant neoplasm of parathyroid gland,Malignant neoplasm of parathyroid gland,Malignant neoplasm of other endocrine glands and related structures,9
C7A0,0,C7A00,Malignant carcinoid tumor of unspecified site,Malignant carcinoid tumor of unspecified site,Malignant carcinoid tumors,9
C7A01,0,C7A010,Malignant carcinoid tumor of the duodenum,Malignant carcinoid tumor of the duodenum,Malignant carcinoid tumors of the small intestine,9
C7A02,0,C7A020,Malignant carcinoid tumor of the appendix,Malignant carcinoid tumor of the appendix,"Malignant carcinoid tumors of the appendix, large intestine, and rectum",9
C7A09,0,C7A090,Malignant carcinoid tumor of the bronchus and lung,Malignant carcinoid tumor of the bronchus and lung,Malignant carcinoid tumors of other sites,9
C7B0,0,C7B00,"Secondary carcinoid tumors, unspecified site","Secondary carcinoid tumors, unspecified site",Secondary carcinoid tumors,9
C76,0,C760,"Malignant neoplasm of head, face and neck","Malignant neoplasm of head, face and neck",Malignant neoplasm of other and ill-defined sites,9
C764,0,C7640,Malignant neoplasm of unspecified upper limb,Malignant neoplasm of unspecified upper limb,Malignant neoplasm of upper limb,9
C765,0,C7650,Malignant neoplasm of unspecified lower limb,Malignant neoplasm of unspecified lower limb,Malignant neoplasm of lower limb,9
C77,0,C770,"Sec and unsp malig neoplasm of nodes of head, face and neck","Secondary and unspecified malignant neoplasm of lymph nodes of head, face and neck",Secondary and unspecified malignant neoplasm of lymph nodes,9
C780,0,C7800,Secondary malignant neoplasm of unspecified lung,Secondary malignant neoplasm of unspecified lung,Secondary malignant neoplasm of lung,9
C783,0,C7830,Secondary malignant neoplasm of unsp respiratory organ,Secondary malignant neoplasm of unspecified respiratory organ,Secondary malignant neoplasm of other and unspecified respiratory organs,9
C788,0,C7880,Secondary malignant neoplasm of unspecified digestive organ,Secondary malignant neoplasm of unspecified digestive organ,Secondary malignant neoplasm of other and unspecified digestive organs,9
C790,0,C7900,Secondary malignant neoplasm of unsp kidney and renal pelvis,Secondary malignant neoplasm of unspecified kidney and renal pelvis,Secondary malignant neoplasm of kidney and renal pelvis,9
C791,0,C7910,Secondary malignant neoplasm of unspecified urinary organs,Secondary malignant neoplasm of unspecified urinary organs,Secondary malignant neoplasm of bladder and other and unspecified urinary organs,9
C794,0,C7940,Secondary malignant neoplasm of unsp part of nervous system,Secondary malignant neoplasm of unspecified part of nervous system,Secondary malignant neoplasm of other and unspecified parts of nervous system,9
C796,0,C7960,Secondary malignant neoplasm of unspecified ovary,Secondary malignant neoplasm of unspecified ovary,Secondary malignant neoplasm of ovary,9
C797,0,C7970,Secondary malignant neoplasm of unspecified adrenal gland,Secondary malignant neoplasm of unspecified adrenal gland,Secondary malignant neoplasm of adrenal gland,9
C80,0,C800,"Disseminated malignant neoplasm, unspecified","Disseminated malignant neoplasm, unspecified",Malignant neoplasm without specification of site,9
C810,0,C8100,"Nodular lymphocyte predominant Hodgkin lymphoma, unsp site","Nodular lymphocyte predominant Hodgkin lymphoma, unspecified site",Nodular lymphocyte predominant Hodgkin lymphoma,9
C811,0,C8110,"Nodular sclerosis Hodgkin lymphoma, unspecified site","Nodular sclerosis Hodgkin lymphoma, unspecified site",Nodular sclerosis Hodgkin lymphoma,9
C812,0,C8120,"Mixed cellularity Hodgkin lymphoma, unspecified site","Mixed cellularity Hodgkin lymphoma, unspecified site",Mixed cellularity Hodgkin lymphoma,9
C813,0,C8130,"Lymphocyte depleted Hodgkin lymphoma, unspecified site","Lymphocyte depleted Hodgkin lymphoma, unspecified site",Lymphocyte depleted Hodgkin lymphoma,9
C814,0,C8140,"Lymphocyte-rich Hodgkin lymphoma, unspecified site","Lymphocyte-rich Hodgkin lymphoma, unspecified site",Lymphocyte-rich Hodgkin lymphoma,9
C817,0,C8170,"Other Hodgkin lymphoma, unspecified site","Other Hodgkin lymphoma, unspecified site",Other Hodgkin lymphoma,9
C819,0,C8190,"Hodgkin lymphoma, unspecified, unspecified site","Hodgkin lymphoma, unspecified, unspecified site","Hodgkin lymphoma, unspecified",9
C820,0,C8200,"Follicular lymphoma grade I, unspecified site","Follicular lymphoma grade I, unspecified site",Follicular lymphoma grade I,9
C821,0,C8210,"Follicular lymphoma grade II, unspecified site","Follicular lymphoma grade II, unspecified site",Follicular lymphoma grade II,9
C822,0,C8220,"Follicular lymphoma grade III, unspecified, unspecified site","Follicular lymphoma grade III, unspecified, unspecified site","Follicular lymphoma grade III, unspecified",9
C823,0,C8230,"Follicular lymphoma grade IIIa, unspecified site","Follicular lymphoma grade IIIa, unspecified site",Follicular lymphoma grade IIIa,9
C824,0,C8240,"Follicular lymphoma grade IIIb, unspecified site","Follicular lymphoma grade IIIb, unspecified site",Follicular lymphoma grade IIIb,9
C825,0,C8250,"Diffuse follicle center lymphoma, unspecified site","Diffuse follicle center lymphoma, unspecified site",Diffuse follicle center lymphoma,9
C826,0,C8260,"Cutaneous follicle center lymphoma, unspecified site","Cutaneous follicle center lymphoma, unspecified site",Cutaneous follicle center lymphoma,9
C828,0,C8280,"Other types of follicular lymphoma, unspecified site","Other types of follicular lymphoma, unspecified site",Other types of follicular lymphoma,9
C829,0,C8290,"Follicular lymphoma, unspecified, unspecified site","Follicular lymphoma, unspecified, unspecified site","Follicular lymphoma, unspecified",9
C830,0,C8300,"Small cell B-cell lymphoma, unspecified site","Small cell B-cell lymphoma, unspecified site",Small cell B-cell lymphoma,9
C831,0,C8310,"Mantle cell lymphoma, unspecified site","Mantle cell lymphoma, unspecified site",Mantle cell lymphoma,9
C833,0,C8330,"Diffuse large B-cell lymphoma, unspecified site","Diffuse large B-cell lymphoma, unspecified site",Diffuse large B-cell lymphoma,9
C835,0,C8350,"Lymphoblastic (diffuse) lymphoma, unspecified site","Lymphoblastic (diffuse) lymphoma, unspecified site",Lymphoblastic (diffuse) lymphoma,9
C837,0,C8370,"Burkitt lymphoma, unspecified site","Burkitt lymphoma, unspecified site",Burkitt lymphoma,9
C838,0,C8380,"Other non-follicular lymphoma, unspecified site","Other non-follicular lymphoma, unspecified site",Other non-follicular lymphoma,9
C839,0,C8390,"Non-follicular (diffuse) lymphoma, unsp, unspecified site","Non-follicular (diffuse) lymphoma, unspecified, unspecified site","Non-follicular (diffuse) lymphoma, unspecified",9
C840,0,C8400,"Mycosis fungoides, unspecified site","Mycosis fungoides, unspecified site",Mycosis fungoides,9
C841,0,C8410,"Sezary disease, unspecified site","Sezary disease, unspecified site",Sezary disease,9
C844,0,C8440,"Peripheral T-cell lymphoma, not classified, unspecified site","Peripheral T-cell lymphoma, not classified, unspecified site","Peripheral T-cell lymphoma, not classified",9
C846,0,C8460,"Anaplastic large cell lymphoma, ALK-positive, unsp site","Anaplastic large cell lymphoma, ALK-positive, unspecified site","Anaplastic large cell lymphoma, ALK-positive",9
C847,0,C8470,"Anaplastic large cell lymphoma, ALK-negative, unsp site","Anaplastic large cell lymphoma, ALK-negative, unspecified site","Anaplastic large cell lymphoma, ALK-negative",9
C84A,0,C84A0,"Cutaneous T-cell lymphoma, unspecified, unspecified site","Cutaneous T-cell lymphoma, unspecified, unspecified site","Cutaneous T-cell lymphoma, unspecified",9
C84Z,0,C84Z0,"Other mature T/NK-cell lymphomas, unspecified site","Other mature T/NK-cell lymphomas, unspecified site",Other mature T/NK-cell lymphomas,9
C849,0,C8490,"Mature T/NK-cell lymphomas, unspecified, unspecified site","Mature T/NK-cell lymphomas, unspecified, unspecified site","Mature T/NK-cell lymphomas, unspecified",9
C851,0,C8510,"Unspecified B-cell lymphoma, unspecified site","Unspecified B-cell lymphoma, unspecified site",Unspecified B-cell lymphoma,9
C852,0,C8520,"Mediastinal (thymic) large B-cell lymphoma, unspecified site","Mediastinal (thymic) large B-cell lymphoma, unspecified site",Mediastinal (thymic) large B-cell lymphoma,9
C858,0,C8580,"Oth types of non-Hodgkin lymphoma, unspecified site","Other specified types of non-Hodgkin lymphoma, unspecified site",Other specified types of non-Hodgkin lymphoma,9
C859,0,C8590,"Non-Hodgkin lymphoma, unspecified, unspecified site","Non-Hodgkin lymphoma, unspecified, unspecified site","Non-Hodgkin lymphoma, unspecified",9
C86,0,C860,"Extranodal NK/T-cell lymphoma, nasal type","Extranodal NK/T-cell lymphoma, nasal type",Other specified types of T/NK-cell lymphoma,9
C88,0,C880,Waldenstrom macroglobulinemia,Waldenstrom macroglobulinemia,Malignant immunoproliferative diseases and certain other B-cell lymphomas,9
C900,0,C9000,Multiple myeloma not having achieved remission,Multiple myeloma not having achieved remission,Multiple myeloma,9
C901,0,C9010,Plasma cell leukemia not having achieved remission,Plasma cell leukemia not having achieved remission,Plasma cell leukemia,9
C902,0,C9020,Extramedullary plasmacytoma not having achieved remission,Extramedullary plasmacytoma not having achieved remission,Extramedullary plasmacytoma,9
C903,0,C9030,Solitary plasmacytoma not having achieved remission,Solitary plasmacytoma not having achieved remission,Solitary plasmacytoma,9
C910,0,C9100,Acute lymphoblastic leukemia not having achieved remission,Acute lymphoblastic leukemia not having achieved remission,Acute lymphoblastic leukemia [ALL],9
C911,0,C9110,Chronic lymphocytic leuk of B-cell type not achieve remis,Chronic lymphocytic leukemia of B-cell type not having achieved remission,Chronic lymphocytic leukemia of B-cell type,9
C913,0,C9130,Prolymphocytic leukemia of B-cell type not achieve remission,Prolymphocytic leukemia of B-cell type not having achieved remission,Prolymphocytic leukemia of B-cell type,9
C914,0,C9140,Hairy cell leukemia not having achieved remission,Hairy cell leukemia not having achieved remission,Hairy cell leukemia,9
C915,0,C9150,Adult T-cell lymph/leuk (HTLV-1-assoc) not achieve remission,Adult T-cell lymphoma/leukemia (HTLV-1-associated) not having achieved remission,Adult T-cell lymphoma/leukemia (HTLV-1-associated),9
C916,0,C9160,Prolymphocytic leukemia of T-cell type not achieve remission,Prolymphocytic leukemia of T-cell type not having achieved remission,Prolymphocytic leukemia of T-cell type,9
C91A,0,C91A0,Mature B-cell leukemia Burkitt-type not achieve remission,Mature B-cell leukemia Burkitt-type not having achieved remission,Mature B-cell leukemia Burkitt-type,9
C91Z,0,C91Z0,Other lymphoid leukemia not having achieved remission,Other lymphoid leukemia not having achieved remission,Other lymphoid leukemia,9
C919,0,C9190,"Lymphoid leukemia, unspecified not having achieved remission","Lymphoid leukemia, unspecified not having achieved remission","Lymphoid leukemia, unspecified",9
C920,0,C9200,"Acute myeloblastic leukemia, not having achieved remission","Acute myeloblastic leukemia, not having achieved remission",Acute myeloblastic leukemia,9
C921,0,C9210,"Chronic myeloid leuk, BCR/ABL-positive, not achieve remis","Chronic myeloid leukemia, BCR/ABL-positive, not having achieved remission","Chronic myeloid leukemia, BCR/ABL-positive",9
C922,0,C9220,"Atyp chronic myeloid leuk, BCR/ABL-neg, not achieve remis","Atypical chronic myeloid leukemia, BCR/ABL-negative, not having achieved remission","Atypical chronic myeloid leukemia, BCR/ABL-negative",9
C923,0,C9230,"Myeloid sarcoma, not having achieved remission","Myeloid sarcoma, not having achieved remission",Myeloid sarcoma,9
C924,0,C9240,"Acute promyelocytic leukemia, not having achieved remission","Acute promyelocytic leukemia, not having achieved remission",Acute promyelocytic leukemia,9
C925,0,C9250,"Acute myelomonocytic leukemia, not having achieved remission","Acute myelomonocytic leukemia, not having achieved remission",Acute myelomonocytic leukemia,9
C926,0,C9260,Acute myeloid leukemia w 11q23-abnormality not achieve remis,Acute myeloid leukemia with 11q23-abnormality not having achieved remission,Acute myeloid leukemia with 11q23-abnormality,9
C92A,0,C92A0,"Acute myeloid leuk w multilin dysplasia, not achieve remis","Acute myeloid leukemia with multilineage dysplasia, not having achieved remission",Acute myeloid leukemia with multilineage dysplasia,9
C92Z,0,C92Z0,Other myeloid leukemia not having achieved remission,Other myeloid leukemia not having achieved remission,Other myeloid leukemia,9
C929,0,C9290,"Myeloid leukemia, unspecified, not having achieved remission","Myeloid leukemia, unspecified, not having achieved remission","Myeloid leukemia, unspecified",9
C930,0,C9300,"Acute monoblastic/monocytic leukemia, not achieve remission","Acute monoblastic/monocytic leukemia, not having achieved remission",Acute monoblastic/monocytic leukemia,9
C931,0,C9310,Chronic myelomonocytic leukemia not achieve remission,Chronic myelomonocytic leukemia not having achieved remission,Chronic myelomonocytic leukemia,9
C933,0,C9330,"Juvenile myelomonocytic leukemia, not achieve remission","Juvenile myelomonocytic leukemia, not having achieved remission",Juvenile myelomonocytic leukemia,9
C93Z,0,C93Z0,"Other monocytic leukemia, not having achieved remission","Other monocytic leukemia, not having achieved remission",Other monocytic leukemia,9
C939,0,C9390,"Monocytic leukemia, unsp, not having achieved remission","Monocytic leukemia, unspecified, not having achieved remission","Monocytic leukemia, unspecified",9
C940,0,C9400,"Acute erythroid leukemia, not having achieved remission","Acute erythroid leukemia, not having achieved remission",Acute erythroid leukemia,9
C942,0,C9420,Acute megakaryoblastic leukemia not achieve remission,Acute megakaryoblastic leukemia not having achieved remission,Acute megakaryoblastic leukemia,9
C943,0,C9430,Mast cell leukemia not having achieved remission,Mast cell leukemia not having achieved remission,Mast cell leukemia,9
C944,0,C9440,Acute panmyelosis w myelofibrosis not achieve remission,Acute panmyelosis with myelofibrosis not having achieved remission,Acute panmyelosis with myelofibrosis,9
C948,0,C9480,Other specified leukemias not having achieved remission,Other specified leukemias not having achieved remission,Other specified leukemias,9
C950,0,C9500,Acute leukemia of unsp cell type not achieve remission,Acute leukemia of unspecified cell type not having achieved remission,Acute leukemia of unspecified cell type,9
C951,0,C9510,Chronic leukemia of unsp cell type not achieve remission,Chronic leukemia of unspecified cell type not having achieved remission,Chronic leukemia of unspecified cell type,9
C959,0,C9590,"Leukemia, unspecified not having achieved remission","Leukemia, unspecified not having achieved remission","Leukemia, unspecified",9
C96,0,C960,Multifocal and multisystemic Langerhans-cell histiocytosis,Multifocal and multisystemic (disseminated) Langerhans-cell histiocytosis,"Other and unspecified malignant neoplasms of lymphoid, hematopoietic and related tissue",9
C962,0,C9620,"Malignant mast cell neoplasm, unspecified","Malignant mast cell neoplasm, unspecified",Malignant mast cell neoplasm,9
D000,0,D0000,"Carcinoma in situ of oral cavity, unspecified site","Carcinoma in situ of oral cavity, unspecified site","Carcinoma in situ of lip, oral cavity and pharynx",9
D01,0,D010,Carcinoma in situ of colon,Carcinoma in situ of colon,Carcinoma in situ of other and unspecified digestive organs,9
D014,0,D0140,Carcinoma in situ of unspecified part of intestine,Carcinoma in situ of unspecified part of intestine,Carcinoma in situ of other and unspecified parts of intestine,9
D02,0,D020,Carcinoma in situ of larynx,Carcinoma in situ of larynx,Carcinoma in situ of middle ear and respiratory system,9
D022,0,D0220,Carcinoma in situ of unspecified bronchus and lung,Carcinoma in situ of unspecified bronchus and lung,Carcinoma in situ of bronchus and lung,9
D03,0,D030,Melanoma in situ of lip,Melanoma in situ of lip,Melanoma in situ,9
D031,0,D0310,"Melanoma in situ of unspecified eyelid, including canthus","Melanoma in situ of unspecified eyelid, including canthus","Melanoma in situ of eyelid, including canthus",9
D032,0,D0320,Melanoma in situ of unsp ear and external auricular canal,Melanoma in situ of unspecified ear and external auricular canal,Melanoma in situ of ear and external auricular canal,9
D033,0,D0330,Melanoma in situ of unspecified part of face,Melanoma in situ of unspecified part of face,Melanoma in situ of other and unspecified parts of face,9
D036,0,D0360,"Melanoma in situ of unsp upper limb, including shoulder","Melanoma in situ of unspecified upper limb, including shoulder","Melanoma in situ of upper limb, including shoulder",9
D037,0,D0370,"Melanoma in situ of unspecified lower limb, including hip","Melanoma in situ of unspecified lower limb, including hip","Melanoma in situ of lower limb, including hip",9
D04,0,D040,Carcinoma in situ of skin of lip,Carcinoma in situ of skin of lip,Carcinoma in situ of skin,9
D041,0,D0410,"Carcinoma in situ of skin of unsp eyelid, including canthus","Carcinoma in situ of skin of unspecified eyelid, including canthus","Carcinoma in situ of skin of eyelid, including canthus",9
D042,0,D0420,Ca in situ skin of unsp ear and external auricular canal,Carcinoma in situ of skin of unspecified ear and external auricular canal,Carcinoma in situ of skin of ear and external auricular canal,9
D043,0,D0430,Carcinoma in situ of skin of unspecified part of face,Carcinoma in situ of skin of unspecified part of face,Carcinoma in situ of skin of other and unspecified parts of face,9
D046,0,D0460,"Ca in situ skin of unsp upper limb, including shoulder","Carcinoma in situ of skin of unspecified upper limb, including shoulder","Carcinoma in situ of skin of upper limb, including shoulder",9
D047,0,D0470,"Carcinoma in situ of skin of unsp lower limb, including hip","Carcinoma in situ of skin of unspecified lower limb, including hip","Carcinoma in situ of skin of lower limb, including hip",9
D050,0,D0500,Lobular carcinoma in situ of unspecified breast,Lobular carcinoma in situ of unspecified breast,Lobular carcinoma in situ of breast,9
D051,0,D0510,Intraductal carcinoma in situ of unspecified breast,Intraductal carcinoma in situ of unspecified breast,Intraductal carcinoma in situ of breast,9
D058,0,D0580,Oth type of carcinoma in situ of unspecified breast,Other specified type of carcinoma in situ of unspecified breast,Other specified type of carcinoma in situ of breast,9
D059,0,D0590,Unspecified type of carcinoma in situ of unspecified breast,Unspecified type of carcinoma in situ of unspecified breast,Unspecified type of carcinoma in situ of breast,9
D06,0,D060,Carcinoma in situ of endocervix,Carcinoma in situ of endocervix,Carcinoma in situ of cervix uteri,9
D07,0,D070,Carcinoma in situ of endometrium,Carcinoma in situ of endometrium,Carcinoma in situ of other and unspecified genital organs,9
D073,0,D0730,Carcinoma in situ of unspecified female genital organs,Carcinoma in situ of unspecified female genital organs,Carcinoma in situ of other and unspecified female genital organs,9
D076,0,D0760,Carcinoma in situ of unspecified male genital organs,Carcinoma in situ of unspecified male genital organs,Carcinoma in situ of other and unspecified male genital organs,9
D09,0,D090,Carcinoma in situ of bladder,Carcinoma in situ of bladder,Carcinoma in situ of other and unspecified sites,9
D091,0,D0910,Carcinoma in situ of unspecified urinary organ,Carcinoma in situ of unspecified urinary organ,Carcinoma in situ of other and unspecified urinary organs,9
D092,0,D0920,Carcinoma in situ of unspecified eye,Carcinoma in situ of unspecified eye,Carcinoma in situ of eye,9
D10,0,D100,Benign neoplasm of lip,Benign neoplasm of lip,Benign neoplasm of mouth and pharynx,9
D103,0,D1030,Benign neoplasm of unspecified part of mouth,Benign neoplasm of unspecified part of mouth,Benign neoplasm of other and unspecified parts of mouth,9
D11,0,D110,Benign neoplasm of parotid gland,Benign neoplasm of parotid gland,Benign neoplasm of major salivary glands,9
D12,0,D120,Benign neoplasm of cecum,Benign neoplasm of cecum,"Benign neoplasm of colon, rectum, anus and anal canal",9
D13,0,D130,Benign neoplasm of esophagus,Benign neoplasm of esophagus,Benign neoplasm of other and ill-defined parts of digestive system,9
D133,0,D1330,Benign neoplasm of unspecified part of small intestine,Benign neoplasm of unspecified part of small intestine,Benign neoplasm of other and unspecified parts of small intestine,9
D14,0,D140,"Benign neoplasm of mid ear, nasl cav and accessory sinuses","Benign neoplasm of middle ear, nasal cavity and accessory sinuses",Benign neoplasm of middle ear and respiratory system,9
D143,0,D1430,Benign neoplasm of unspecified bronchus and lung,Benign neoplasm of unspecified bronchus and lung,Benign neoplasm of bronchus and lung,9
D15,0,D150,Benign neoplasm of thymus,Benign neoplasm of thymus,Benign neoplasm of other and unspecified intrathoracic organs,9
D160,0,D1600,Benign neoplasm of scapula and long bones of unsp upper limb,Benign neoplasm of scapula and long bones of unspecified upper limb,Benign neoplasm of scapula and long bones of upper limb,9
D161,0,D1610,Benign neoplasm of short bones of unspecified upper limb,Benign neoplasm of short bones of unspecified upper limb,Benign neoplasm of short bones of upper limb,9
D162,0,D1620,Benign neoplasm of long bones of unspecified lower limb,Benign neoplasm of long bones of unspecified lower limb,Benign neoplasm of long bones of lower limb,9
D163,0,D1630,Benign neoplasm of short bones of unspecified lower limb,Benign neoplasm of short bones of unspecified lower limb,Benign neoplasm of short bones of lower limb,9
D17,0,D170,"Ben lipomatous neoplm of skin, subcu of head, face and neck","Benign lipomatous neoplasm of skin and subcutaneous tissue of head, face and neck",Benign lipomatous neoplasm,9
D172,0,D1720,"Benign lipomatous neoplasm of skin, subcu of unsp limb",Benign lipomatous neoplasm of skin and subcutaneous tissue of unspecified limb,Benign lipomatous neoplasm of skin and subcutaneous tissue of limb,9
D173,0,D1730,"Benign lipomatous neoplasm of skin, subcu of unsp sites",Benign lipomatous neoplasm of skin and subcutaneous tissue of unspecified sites,Benign lipomatous neoplasm of skin and subcutaneous tissue of other and unspecified sites,9
D180,0,D1800,Hemangioma unspecified site,Hemangioma unspecified site,Hemangioma,9
D19,0,D190,Benign neoplasm of mesothelial tissue of pleura,Benign neoplasm of mesothelial tissue of pleura,Benign neoplasm of mesothelial tissue,9
D20,0,D200,Benign neoplasm of soft tissue of retroperitoneum,Benign neoplasm of soft tissue of retroperitoneum,Benign neoplasm of soft tissue of retroperitoneum and peritoneum,9
D21,0,D210,"Benign neoplasm of connctv/soft tiss of head, face and neck","Benign neoplasm of connective and other soft tissue of head, face and neck",Other benign neoplasms of connective and other soft tissue,9
D211,0,D2110,"Ben neoplm of connctv/soft tiss of unsp upr limb, inc shldr","Benign neoplasm of connective and other soft tissue of unspecified upper limb, including shoulder","Benign neoplasm of connective and other soft tissue of upper limb, including shoulder",9
D212,0,D2120,"Ben neoplm of connctv/soft tiss of unsp lower limb, inc hip","Benign neoplasm of connective and other soft tissue of unspecified lower limb, including hip","Benign neoplasm of connective and other soft tissue of lower limb, including hip",9
D22,0,D220,Melanocytic nevi of lip,Melanocytic nevi of lip,Melanocytic nevi,9
D221,0,D2210,"Melanocytic nevi of unspecified eyelid, including canthus","Melanocytic nevi of unspecified eyelid, including canthus","Melanocytic nevi of eyelid, including canthus",9
D222,0,D2220,Melanocytic nevi of unsp ear and external auricular canal,Melanocytic nevi of unspecified ear and external auricular canal,Melanocytic nevi of ear and external auricular canal,9
D223,0,D2230,Melanocytic nevi of unspecified part of face,Melanocytic nevi of unspecified part of face,Melanocytic nevi of other and unspecified parts of face,9
D226,0,D2260,"Melanocytic nevi of unsp upper limb, including shoulder","Melanocytic nevi of unspecified upper limb, including shoulder","Melanocytic nevi of upper limb, including shoulder",9
D227,0,D2270,"Melanocytic nevi of unspecified lower limb, including hip","Melanocytic nevi of unspecified lower limb, including hip","Melanocytic nevi of lower limb, including hip",9
D23,0,D230,Other benign neoplasm of skin of lip,Other benign neoplasm of skin of lip,Other benign neoplasms of skin,9
D231,0,D2310,"Oth benign neoplasm skin/ unsp eyelid, including canthus","Other benign neoplasm of skin of unspecified eyelid, including canthus","Other benign neoplasm of skin of eyelid, including canthus",9
D232,0,D2320,Oth benign neoplasm skin/ unsp ear and external auric canal,Other benign neoplasm of skin of unspecified ear and external auricular canal,Other benign neoplasm of skin of ear and external auricular canal,9
D233,0,D2330,Other benign neoplasm of skin of unspecified part of face,Other benign neoplasm of skin of unspecified part of face,Other benign neoplasm of skin of other and unspecified parts of face,9
D236,0,D2360,"Oth benign neoplasm skin/ unsp upper limb, inc shoulder","Other benign neoplasm of skin of unspecified upper limb, including shoulder","Other benign neoplasm of skin of upper limb, including shoulder",9
D237,0,D2370,"Oth benign neoplasm skin/ unsp lower limb, including hip","Other benign neoplasm of skin of unspecified lower limb, including hip","Other benign neoplasm of skin of lower limb, including hip",9
D25,0,D250,Submucous leiomyoma of uterus,Submucous leiomyoma of uterus,Leiomyoma of uterus,9
D26,0,D260,Other benign neoplasm of cervix uteri,Other benign neoplasm of cervix uteri,Other benign neoplasms of uterus,9
D27,0,D270,Benign neoplasm of right ovary,Benign neoplasm of right ovary,Benign neoplasm of ovary,9
D28,0,D280,Benign neoplasm of vulva,Benign neoplasm of vulva,Benign neoplasm of other and unspecified female genital organs,9
D29,0,D290,Benign neoplasm of penis,Benign neoplasm of penis,Benign neoplasm of male genital organs,9
D292,0,D2920,Benign neoplasm of unspecified testis,Benign neoplasm of unspecified testis,Benign neoplasm of testis,9
D293,0,D2930,Benign neoplasm of unspecified epididymis,Benign neoplasm of unspecified epididymis,Benign neoplasm of epididymis,9
D300,0,D3000,Benign neoplasm of unspecified kidney,Benign neoplasm of unspecified kidney,Benign neoplasm of kidney,9
D301,0,D3010,Benign neoplasm of unspecified renal pelvis,Benign neoplasm of unspecified renal pelvis,Benign neoplasm of renal pelvis,9
D302,0,D3020,Benign neoplasm of unspecified ureter,Benign neoplasm of unspecified ureter,Benign neoplasm of ureter,9
D310,0,D3100,Benign neoplasm of unspecified conjunctiva,Benign neoplasm of unspecified conjunctiva,Benign neoplasm of conjunctiva,9
D311,0,D3110,Benign neoplasm of unspecified cornea,Benign neoplasm of unspecified cornea,Benign neoplasm of cornea,9
D312,0,D3120,Benign neoplasm of unspecified retina,Benign neoplasm of unspecified retina,Benign neoplasm of retina,9
D313,0,D3130,Benign neoplasm of unspecified choroid,Benign neoplasm of unspecified choroid,Benign neoplasm of choroid,9
D314,0,D3140,Benign neoplasm of unspecified ciliary body,Benign neoplasm of unspecified ciliary body,Benign neoplasm of ciliary body,9
D315,0,D3150,Benign neoplasm of unspecified lacrimal gland and duct,Benign neoplasm of unspecified lacrimal gland and duct,Benign neoplasm of lacrimal gland and duct,9
D316,0,D3160,Benign neoplasm of unspecified site of unspecified orbit,Benign neoplasm of unspecified site of unspecified orbit,Benign neoplasm of unspecified site of orbit,9
D319,0,D3190,Benign neoplasm of unspecified part of unspecified eye,Benign neoplasm of unspecified part of unspecified eye,Benign neoplasm of unspecified part of eye,9
D32,0,D320,Benign neoplasm of cerebral meninges,Benign neoplasm of cerebral meninges,Benign neoplasm of meninges,9
D33,0,D330,"Benign neoplasm of brain, supratentorial","Benign neoplasm of brain, supratentorial",Benign neoplasm of brain and other parts of central nervous system,9
D350,0,D3500,Benign neoplasm of unspecified adrenal gland,Benign neoplasm of unspecified adrenal gland,Benign neoplasm of adrenal gland,9
D36,0,D360,Benign neoplasm of lymph nodes,Benign neoplasm of lymph nodes,Benign neoplasm of other and unspecified sites,9
D361,0,D3610,"Benign neoplasm of prph nerves and autonm nervous sys, unsp","Benign neoplasm of peripheral nerves and autonomic nervous system, unspecified",Benign neoplasm of peripheral nerves and autonomic nervous system,9
D3A0,0,D3A00,Benign carcinoid tumor of unspecified site,Benign carcinoid tumor of unspecified site,Benign carcinoid tumors,9
D3A01,0,D3A010,Benign carcinoid tumor of the duodenum,Benign carcinoid tumor of the duodenum,Benign carcinoid tumors of the small intestine,9
B26,3,B263,Mumps pancreatitis,Mumps pancreatitis,Mumps,9
D3A02,0,D3A020,Benign carcinoid tumor of the appendix,Benign carcinoid tumor of the appendix,"Benign carcinoid tumors of the appendix, large intestine, and rectum",9
D3A09,0,D3A090,Benign carcinoid tumor of the bronchus and lung,Benign carcinoid tumor of the bronchus and lung,Benign carcinoid tumors of other sites,9
D3703,0,D37030,Neoplasm of uncertain behavior of the parotid salivary gland,Neoplasm of uncertain behavior of the parotid salivary glands,Neoplasm of uncertain behavior of the major salivary glands,9
D38,0,D380,Neoplasm of uncertain behavior of larynx,Neoplasm of uncertain behavior of larynx,Neoplasm of uncertain behavior of middle ear and respiratory and intrathoracic organs,9
D39,0,D390,Neoplasm of uncertain behavior of uterus,Neoplasm of uncertain behavior of uterus,Neoplasm of uncertain behavior of female genital organs,9
D391,0,D3910,Neoplasm of uncertain behavior of unspecified ovary,Neoplasm of uncertain behavior of unspecified ovary,Neoplasm of uncertain behavior of ovary,9
D40,0,D400,Neoplasm of uncertain behavior of prostate,Neoplasm of uncertain behavior of prostate,Neoplasm of uncertain behavior of male genital organs,9
D401,0,D4010,Neoplasm of uncertain behavior of unspecified testis,Neoplasm of uncertain behavior of unspecified testis,Neoplasm of uncertain behavior of testis,9
D410,0,D4100,Neoplasm of uncertain behavior of unspecified kidney,Neoplasm of uncertain behavior of unspecified kidney,Neoplasm of uncertain behavior of kidney,9
D411,0,D4110,Neoplasm of uncertain behavior of unspecified renal pelvis,Neoplasm of uncertain behavior of unspecified renal pelvis,Neoplasm of uncertain behavior of renal pelvis,9
D412,0,D4120,Neoplasm of uncertain behavior of unspecified ureter,Neoplasm of uncertain behavior of unspecified ureter,Neoplasm of uncertain behavior of ureter,9
D42,0,D420,Neoplasm of uncertain behavior of cerebral meninges,Neoplasm of uncertain behavior of cerebral meninges,Neoplasm of uncertain behavior of meninges,9
D43,0,D430,"Neoplasm of uncertain behavior of brain, supratentorial","Neoplasm of uncertain behavior of brain, supratentorial",Neoplasm of uncertain behavior of brain and central nervous system,9
D44,0,D440,Neoplasm of uncertain behavior of thyroid gland,Neoplasm of uncertain behavior of thyroid gland,Neoplasm of uncertain behavior of endocrine glands,9
D441,0,D4410,Neoplasm of uncertain behavior of unspecified adrenal gland,Neoplasm of uncertain behavior of unspecified adrenal gland,Neoplasm of uncertain behavior of adrenal gland,9
D46,0,D460,"Refractory anemia without ring sideroblasts, so stated","Refractory anemia without ring sideroblasts, so stated",Myelodysplastic syndromes,9
D462,0,D4620,"Refractory anemia with excess of blasts, unspecified","Refractory anemia with excess of blasts, unspecified",Refractory anemia with excess of blasts [RAEB],9
D48,0,D480,Neoplasm of uncertain behavior of bone/artic cartl,Neoplasm of uncertain behavior of bone and articular cartilage,Neoplasm of uncertain behavior of other and unspecified sites,9
D486,0,D4860,Neoplasm of uncertain behavior of unspecified breast,Neoplasm of uncertain behavior of unspecified breast,Neoplasm of uncertain behavior of breast,9
D49,0,D490,Neoplasm of unspecified behavior of digestive system,Neoplasm of unspecified behavior of digestive system,Neoplasms of unspecified behavior,9
D50,0,D500,Iron deficiency anemia secondary to blood loss (chronic),Iron deficiency anemia secondary to blood loss (chronic),Iron deficiency anemia,9
D51,0,D510,Vitamin B12 defic anemia due to intrinsic factor deficiency,Vitamin B12 deficiency anemia due to intrinsic factor deficiency,Vitamin B12 deficiency anemia,9
D52,0,D520,Dietary folate deficiency anemia,Dietary folate deficiency anemia,Folate deficiency anemia,9
D53,0,D530,Protein deficiency anemia,Protein deficiency anemia,Other nutritional anemias,9
D55,0,D550,Anemia due to glucose-6-phosphate dehydrogenase deficiency,Anemia due to glucose-6-phosphate dehydrogenase [G6PD] deficiency,Anemia due to enzyme disorders,9
D56,0,D560,Alpha thalassemia,Alpha thalassemia,Thalassemia,9
D570,0,D5700,"Hb-SS disease with crisis, unspecified","Hb-SS disease with crisis, unspecified",Hb-SS disease with crisis,9
D572,0,D5720,Sickle-cell/Hb-C disease without crisis,Sickle-cell/Hb-C disease without crisis,Sickle-cell/Hb-C disease,9
D574,0,D5740,Sickle-cell thalassemia without crisis,Sickle-cell thalassemia without crisis,Sickle-cell thalassemia,9
D578,0,D5780,Other sickle-cell disorders without crisis,Other sickle-cell disorders without crisis,Other sickle-cell disorders,9
D58,0,D580,Hereditary spherocytosis,Hereditary spherocytosis,Other hereditary hemolytic anemias,9
D59,0,D590,Drug-induced autoimmune hemolytic anemia,Drug-induced autoimmune hemolytic anemia,Acquired hemolytic anemia,9
D60,0,D600,Chronic acquired pure red cell aplasia,Chronic acquired pure red cell aplasia,Acquired pure red cell aplasia [erythroblastopenia],9
D6181,0,D61810,Antineoplastic chemotherapy induced pancytopenia,Antineoplastic chemotherapy induced pancytopenia,Pancytopenia,9
D63,0,D630,Anemia in neoplastic disease,Anemia in neoplastic disease,Anemia in chronic diseases classified elsewhere,9
D64,0,D640,Hereditary sideroblastic anemia,Hereditary sideroblastic anemia,Other anemias,9
D68,0,D680,Von Willebrand's disease,Von Willebrand's disease,Other coagulation defects,9
D69,0,D690,Allergic purpura,Allergic purpura,Purpura and other hemorrhagic conditions,9
D70,0,D700,Congenital agranulocytosis,Congenital agranulocytosis,Neutropenia,9
D72,0,D720,Genetic anomalies of leukocytes,Genetic anomalies of leukocytes,Other disorders of white blood cells,9
D7281,0,D72810,Lymphocytopenia,Lymphocytopenia,Decreased white blood cell count,9
D7282,0,D72820,Lymphocytosis (symptomatic),Lymphocytosis (symptomatic),Elevated white blood cell count,9
D73,0,D730,Hyposplenism,Hyposplenism,Diseases of spleen,9
D74,0,D740,Congenital methemoglobinemia,Congenital methemoglobinemia,Methemoglobinemia,9
D75,0,D750,Familial erythrocytosis,Familial erythrocytosis,Other and unspecified diseases of blood and blood-forming organs,9
D80,0,D800,Hereditary hypogammaglobulinemia,Hereditary hypogammaglobulinemia,Immunodeficiency with predominantly antibody defects,9
D81,0,D810,Severe combined immunodeficiency with reticular dysgenesis,Severe combined immunodeficiency [SCID] with reticular dysgenesis,Combined immunodeficiencies,9
D8181,0,D81810,Biotinidase deficiency,Biotinidase deficiency,Biotin-dependent carboxylase deficiency,9
D82,0,D820,Wiskott-Aldrich syndrome,Wiskott-Aldrich syndrome,Immunodeficiency associated with other major defects,9
D83,0,D830,Com variab immunodef w predom abnlt of B-cell nums & functn,Common variable immunodeficiency with predominant abnormalities of B-cell numbers and function,Common variable immunodeficiency,9
D84,0,D840,Lymphocyte function antigen-1 [LFA-1] defect,Lymphocyte function antigen-1 [LFA-1] defect,Other immunodeficiencies,9
D86,0,D860,Sarcoidosis of lung,Sarcoidosis of lung,Sarcoidosis,9
D89,0,D890,Polyclonal hypergammaglobulinemia,Polyclonal hypergammaglobulinemia,"Other disorders involving the immune mechanism, not elsewhere classified",9
D894,0,D8940,"Mast cell activation, unspecified","Mast cell activation, unspecified",Mast cell activation syndrome and related disorders,9
D8981,0,D89810,Acute graft-versus-host disease,Acute graft-versus-host disease,Graft-versus-host disease,9
E00,0,E000,"Congenital iodine-deficiency syndrome, neurological type","Congenital iodine-deficiency syndrome, neurological type",Congenital iodine-deficiency syndrome,9
E01,0,E010,Iodine-deficiency related diffuse (endemic) goiter,Iodine-deficiency related diffuse (endemic) goiter,Iodine-deficiency related thyroid disorders and allied conditions,9
E03,0,E030,Congenital hypothyroidism with diffuse goiter,Congenital hypothyroidism with diffuse goiter,Other hypothyroidism,9
E04,0,E040,Nontoxic diffuse goiter,Nontoxic diffuse goiter,Other nontoxic goiter,9
E050,0,E0500,Thyrotoxicosis w diffuse goiter w/o thyrotoxic crisis,Thyrotoxicosis with diffuse goiter without thyrotoxic crisis or storm,Thyrotoxicosis with diffuse goiter,9
E051,0,E0510,Thyrotxcosis w toxic sing thyroid nodule w/o thyrotxc crisis,Thyrotoxicosis with toxic single thyroid nodule without thyrotoxic crisis or storm,Thyrotoxicosis with toxic single thyroid nodule,9
E052,0,E0520,Thyrotxcosis w toxic multinod goiter w/o thyrotoxic crisis,Thyrotoxicosis with toxic multinodular goiter without thyrotoxic crisis or storm,Thyrotoxicosis with toxic multinodular goiter,9
E053,0,E0530,Thyrotxcosis from ectopic thyroid tissue w/o thyrotxc crisis,Thyrotoxicosis from ectopic thyroid tissue without thyrotoxic crisis or storm,Thyrotoxicosis from ectopic thyroid tissue,9
E054,0,E0540,Thyrotoxicosis factitia without thyrotoxic crisis or storm,Thyrotoxicosis factitia without thyrotoxic crisis or storm,Thyrotoxicosis factitia,9
E058,0,E0580,Other thyrotoxicosis without thyrotoxic crisis or storm,Other thyrotoxicosis without thyrotoxic crisis or storm,Other thyrotoxicosis,9
E059,0,E0590,"Thyrotoxicosis, unsp without thyrotoxic crisis or storm","Thyrotoxicosis, unspecified without thyrotoxic crisis or storm","Thyrotoxicosis, unspecified",9
E06,0,E060,Acute thyroiditis,Acute thyroiditis,Thyroiditis,9
E07,0,E070,Hypersecretion of calcitonin,Hypersecretion of calcitonin,Other disorders of thyroid,9
E080,0,E0800,Diab d/t undrl cond w hyprosm w/o nonket hyprgly-hypros coma,Diabetes mellitus due to underlying condition with hyperosmolarity without nonketotic hyperglycemic-hyperosmolar coma (NKHHC),Diabetes mellitus due to underlying condition with hyperosmolarity,9
E081,0,E0810,Diabetes due to underlying condition w ketoacidosis w/o coma,Diabetes mellitus due to underlying condition with ketoacidosis without coma,Diabetes mellitus due to underlying condition with ketoacidosis,9
E084,0,E0840,"Diabetes due to underlying condition w diabetic neurop, unsp","Diabetes mellitus due to underlying condition with diabetic neuropathy, unspecified",Diabetes mellitus due to underlying condition with neurological complications,9
E0861,0,E08610,Diabetes due to undrl cond w diabetic neuropathic arthrop,Diabetes mellitus due to underlying condition with diabetic neuropathic arthropathy,Diabetes mellitus due to underlying condition with diabetic arthropathy,9
E0862,0,E08620,Diabetes due to underlying condition w diabetic dermatitis,Diabetes mellitus due to underlying condition with diabetic dermatitis,Diabetes mellitus due to underlying condition with skin complications,9
E0863,0,E08630,Diabetes due to underlying condition w periodontal disease,Diabetes mellitus due to underlying condition with periodontal disease,Diabetes mellitus due to underlying condition with oral complications,9
E090,0,E0900,Drug/chem diab w hyprosm w/o nonket hyprgly-hypros coma,Drug or chemical induced diabetes mellitus with hyperosmolarity without nonketotic hyperglycemic-hyperosmolar coma (NKHHC),Drug or chemical induced diabetes mellitus with hyperosmolarity,9
E091,0,E0910,Drug/chem diabetes mellitus w ketoacidosis w/o coma,Drug or chemical induced diabetes mellitus with ketoacidosis without coma,Drug or chemical induced diabetes mellitus with ketoacidosis,9
E094,0,E0940,"Drug/chem diabetes w neuro comp w diabetic neuropathy, unsp","Drug or chemical induced diabetes mellitus with neurological complications with diabetic neuropathy, unspecified",Drug or chemical induced diabetes mellitus with neurological complications,9
E0961,0,E09610,Drug/chem diabetes w diabetic neuropathic arthropathy,Drug or chemical induced diabetes mellitus with diabetic neuropathic arthropathy,Drug or chemical induced diabetes mellitus with diabetic arthropathy,9
E0962,0,E09620,Drug/chem diabetes mellitus w diabetic dermatitis,Drug or chemical induced diabetes mellitus with diabetic dermatitis,Drug or chemical induced diabetes mellitus with skin complications,9
E0963,0,E09630,Drug/chem diabetes mellitus w periodontal disease,Drug or chemical induced diabetes mellitus with periodontal disease,Drug or chemical induced diabetes mellitus with oral complications,9
E101,0,E1010,Type 1 diabetes mellitus with ketoacidosis without coma,Type 1 diabetes mellitus with ketoacidosis without coma,Type 1 diabetes mellitus with ketoacidosis,9
E104,0,E1040,"Type 1 diabetes mellitus with diabetic neuropathy, unsp","Type 1 diabetes mellitus with diabetic neuropathy, unspecified",Type 1 diabetes mellitus with neurological complications,9
E1061,0,E10610,Type 1 diabetes mellitus w diabetic neuropathic arthropathy,Type 1 diabetes mellitus with diabetic neuropathic arthropathy,Type 1 diabetes mellitus with diabetic arthropathy,9
E1062,0,E10620,Type 1 diabetes mellitus with diabetic dermatitis,Type 1 diabetes mellitus with diabetic dermatitis,Type 1 diabetes mellitus with skin complications,9
E1063,0,E10630,Type 1 diabetes mellitus with periodontal disease,Type 1 diabetes mellitus with periodontal disease,Type 1 diabetes mellitus with oral complications,9
E7112,0,E71120,Methylmalonic acidemia,Methylmalonic acidemia,Disorders of propionate metabolism,9
E110,0,E1100,Type 2 diab w hyprosm w/o nonket hyprgly-hypros coma (NKHHC),Type 2 diabetes mellitus with hyperosmolarity without nonketotic hyperglycemic-hyperosmolar coma (NKHHC),Type 2 diabetes mellitus with hyperosmolarity,9
E111,0,E1110,Type 2 diabetes mellitus with ketoacidosis without coma,Type 2 diabetes mellitus with ketoacidosis without coma,Type 2 diabetes mellitus with ketoacidosis,9
E114,0,E1140,"Type 2 diabetes mellitus with diabetic neuropathy, unsp","Type 2 diabetes mellitus with diabetic neuropathy, unspecified",Type 2 diabetes mellitus with neurological complications,9
E1161,0,E11610,Type 2 diabetes mellitus w diabetic neuropathic arthropathy,Type 2 diabetes mellitus with diabetic neuropathic arthropathy,Type 2 diabetes mellitus with diabetic arthropathy,9
E1162,0,E11620,Type 2 diabetes mellitus with diabetic dermatitis,Type 2 diabetes mellitus with diabetic dermatitis,Type 2 diabetes mellitus with skin complications,9
E1163,0,E11630,Type 2 diabetes mellitus with periodontal disease,Type 2 diabetes mellitus with periodontal disease,Type 2 diabetes mellitus with oral complications,9
E130,0,E1300,Oth diab w hyprosm w/o nonket hyprgly-hypros coma (NKHHC),Other specified diabetes mellitus with hyperosmolarity without nonketotic hyperglycemic-hyperosmolar coma (NKHHC),Other specified diabetes mellitus with hyperosmolarity,9
E131,0,E1310,Oth diabetes mellitus with ketoacidosis without coma,Other specified diabetes mellitus with ketoacidosis without coma,Other specified diabetes mellitus with ketoacidosis,9
E134,0,E1340,"Oth diabetes mellitus with diabetic neuropathy, unspecified","Other specified diabetes mellitus with diabetic neuropathy, unspecified",Other specified diabetes mellitus with neurological complications,9
E1361,0,E13610,Oth diabetes mellitus with diabetic neuropathic arthropathy,Other specified diabetes mellitus with diabetic neuropathic arthropathy,Other specified diabetes mellitus with diabetic arthropathy,9
E1362,0,E13620,Other specified diabetes mellitus with diabetic dermatitis,Other specified diabetes mellitus with diabetic dermatitis,Other specified diabetes mellitus with skin complications,9
E1363,0,E13630,Other specified diabetes mellitus with periodontal disease,Other specified diabetes mellitus with periodontal disease,Other specified diabetes mellitus with oral complications,9
E16,0,E160,Drug-induced hypoglycemia without coma,Drug-induced hypoglycemia without coma,Other disorders of pancreatic internal secretion,9
E20,0,E200,Idiopathic hypoparathyroidism,Idiopathic hypoparathyroidism,Hypoparathyroidism,9
E21,0,E210,Primary hyperparathyroidism,Primary hyperparathyroidism,Hyperparathyroidism and other disorders of parathyroid gland,9
E22,0,E220,Acromegaly and pituitary gigantism,Acromegaly and pituitary gigantism,Hyperfunction of pituitary gland,9
E23,0,E230,Hypopituitarism,Hypopituitarism,Hypofunction and other disorders of the pituitary gland,9
E24,0,E240,Pituitary-dependent Cushing's disease,Pituitary-dependent Cushing's disease,Cushing's syndrome,9
E25,0,E250,Congenital adrenogenital disorders assoc w enzyme deficiency,Congenital adrenogenital disorders associated with enzyme deficiency,Adrenogenital disorders,9
E27,0,E270,Other adrenocortical overactivity,Other adrenocortical overactivity,Other disorders of adrenal gland,9
E274,0,E2740,Unspecified adrenocortical insufficiency,Unspecified adrenocortical insufficiency,Other and unspecified adrenocortical insufficiency,9
E28,0,E280,Estrogen excess,Estrogen excess,Ovarian dysfunction,9
E2831,0,E28310,Symptomatic premature menopause,Symptomatic premature menopause,Premature menopause,9
E29,0,E290,Testicular hyperfunction,Testicular hyperfunction,Testicular dysfunction,9
E30,0,E300,Delayed puberty,Delayed puberty,"Disorders of puberty, not elsewhere classified",9
E31,0,E310,Autoimmune polyglandular failure,Autoimmune polyglandular failure,Polyglandular dysfunction,9
E312,0,E3120,"Multiple endocrine neoplasia [MEN] syndrome, unspecified","Multiple endocrine neoplasia [MEN] syndrome, unspecified",Multiple endocrine neoplasia [MEN] syndromes,9
E32,0,E320,Persistent hyperplasia of thymus,Persistent hyperplasia of thymus,Diseases of thymus,9
E34,0,E340,Carcinoid syndrome,Carcinoid syndrome,Other endocrine disorders,9
E345,0,E3450,"Androgen insensitivity syndrome, unspecified","Androgen insensitivity syndrome, unspecified",Androgen insensitivity syndrome,9
E44,0,E440,Moderate protein-calorie malnutrition,Moderate protein-calorie malnutrition,Protein-calorie malnutrition of moderate and mild degree,9
E50,0,E500,Vitamin A deficiency with conjunctival xerosis,Vitamin A deficiency with conjunctival xerosis,Vitamin A deficiency,9
E53,0,E530,Riboflavin deficiency,Riboflavin deficiency,Deficiency of other B group vitamins,9
E55,0,E550,"Rickets, active","Rickets, active",Vitamin D deficiency,9
E56,0,E560,Deficiency of vitamin E,Deficiency of vitamin E,Other vitamin deficiencies,9
E61,0,E610,Copper deficiency,Copper deficiency,Deficiency of other nutrient elements,9
E63,0,E630,Essential fatty acid [EFA] deficiency,Essential fatty acid [EFA] deficiency,Other nutritional deficiencies,9
E64,0,E640,Sequelae of protein-calorie malnutrition,Sequelae of protein-calorie malnutrition,Sequelae of malnutrition and other nutritional deficiencies,9
E67,0,E670,Hypervitaminosis A,Hypervitaminosis A,Other hyperalimentation,9
E70,0,E700,Classical phenylketonuria,Classical phenylketonuria,Disorders of aromatic amino-acid metabolism,9
E702,0,E7020,"Disorder of tyrosine metabolism, unspecified","Disorder of tyrosine metabolism, unspecified",Disorders of tyrosine metabolism,9
E703,0,E7030,"Albinism, unspecified","Albinism, unspecified",Albinism,9
E7031,0,E70310,X-linked ocular albinism,X-linked ocular albinism,Ocular albinism,9
E7032,0,E70320,Tyrosinase negative oculocutaneous albinism,Tyrosinase negative oculocutaneous albinism,Oculocutaneous albinism,9
E7033,0,E70330,Chediak-Higashi syndrome,Chediak-Higashi syndrome,Albinism with hematologic abnormality,9
E704,0,E7040,"Disorders of histidine metabolism, unspecified","Disorders of histidine metabolism, unspecified",Disorders of histidine metabolism,9
E71,0,E710,Maple-syrup-urine disease,Maple-syrup-urine disease,Disorders of branched-chain amino-acid metabolism and fatty-acid metabolism,9
E7111,0,E71110,Isovaleric acidemia,Isovaleric acidemia,Branched-chain organic acidurias,9
E713,0,E7130,"Disorder of fatty-acid metabolism, unspecified","Disorder of fatty-acid metabolism, unspecified",Disorders of fatty-acid metabolism,9
E7131,0,E71310,Long chain/very long chain acyl CoA dehydrogenase deficiency,Long chain/very long chain acyl CoA dehydrogenase deficiency,Disorders of fatty-acid oxidation,9
E714,0,E7140,"Disorder of carnitine metabolism, unspecified","Disorder of carnitine metabolism, unspecified",Disorders of carnitine metabolism,9
E7144,0,E71440,Ruvalcaba-Myhre-Smith syndrome,Ruvalcaba-Myhre-Smith syndrome,Other secondary carnitine deficiency,9
E715,0,E7150,"Peroxisomal disorder, unspecified","Peroxisomal disorder, unspecified",Peroxisomal disorders,9
E7151,0,E71510,Zellweger syndrome,Zellweger syndrome,Disorders of peroxisome biogenesis,9
E7152,0,E71520,Childhood cerebral X-linked adrenoleukodystrophy,Childhood cerebral X-linked adrenoleukodystrophy,X-linked adrenoleukodystrophy,9
E7154,0,E71540,Rhizomelic chondrodysplasia punctata,Rhizomelic chondrodysplasia punctata,Other peroxisomal disorders,9
E720,0,E7200,"Disorders of amino-acid transport, unspecified","Disorders of amino-acid transport, unspecified",Disorders of amino-acid transport,9
E721,0,E7210,"Disorders of sulfur-bearing amino-acid metabolism, unsp","Disorders of sulfur-bearing amino-acid metabolism, unspecified",Disorders of sulfur-bearing amino-acid metabolism,9
E722,0,E7220,"Disorder of urea cycle metabolism, unspecified","Disorder of urea cycle metabolism, unspecified",Disorders of urea cycle metabolism,9
E725,0,E7250,"Disorder of glycine metabolism, unspecified","Disorder of glycine metabolism, unspecified",Disorders of glycine metabolism,9
E73,0,E730,Congenital lactase deficiency,Congenital lactase deficiency,Lactose intolerance,9
E740,0,E7400,"Glycogen storage disease, unspecified","Glycogen storage disease, unspecified",Glycogen storage disease,9
E741,0,E7410,"Disorder of fructose metabolism, unspecified","Disorder of fructose metabolism, unspecified",Disorders of fructose metabolism,9
E742,0,E7420,"Disorders of galactose metabolism, unspecified","Disorders of galactose metabolism, unspecified",Disorders of galactose metabolism,9
E750,0,E7500,"GM2 gangliosidosis, unspecified","GM2 gangliosidosis, unspecified",GM2 gangliosidosis,9
E751,0,E7510,Unspecified gangliosidosis,Unspecified gangliosidosis,Other and unspecified gangliosidosis,9
E7524,0,E75240,Niemann-Pick disease type A,Niemann-Pick disease type A,Niemann-Pick disease,9
E7621,0,E76210,Morquio A mucopolysaccharidoses,Morquio A mucopolysaccharidoses,Morquio mucopolysaccharidoses,9
E77,0,E770,Defects in post-translational mod of lysosomal enzymes,Defects in post-translational modification of lysosomal enzymes,Disorders of glycoprotein metabolism,9
E780,0,E7800,"Pure hypercholesterolemia, unspecified","Pure hypercholesterolemia, unspecified",Pure hypercholesterolemia,9
E787,0,E7870,"Disorder of bile acid and cholesterol metabolism, unsp","Disorder of bile acid and cholesterol metabolism, unspecified",Disorders of bile acid and cholesterol metabolism,9
E79,0,E790,Hyperuricemia w/o signs of inflam arthrit and tophaceous dis,Hyperuricemia without signs of inflammatory arthritis and tophaceous disease,Disorders of purine and pyrimidine metabolism,9
E80,0,E800,Hereditary erythropoietic porphyria,Hereditary erythropoietic porphyria,Disorders of porphyrin and bilirubin metabolism,9
E802,0,E8020,Unspecified porphyria,Unspecified porphyria,Other and unspecified porphyria,9
E830,0,E8300,"Disorder of copper metabolism, unspecified","Disorder of copper metabolism, unspecified",Disorders of copper metabolism,9
E831,0,E8310,"Disorder of iron metabolism, unspecified","Disorder of iron metabolism, unspecified",Disorders of iron metabolism,9
E8311,0,E83110,Hereditary hemochromatosis,Hereditary hemochromatosis,Hemochromatosis,9
E833,0,E8330,"Disorder of phosphorus metabolism, unspecified","Disorder of phosphorus metabolism, unspecified",Disorders of phosphorus metabolism and phosphatases,9
E834,0,E8340,"Disorders of magnesium metabolism, unspecified","Disorders of magnesium metabolism, unspecified",Disorders of magnesium metabolism,9
E835,0,E8350,Unspecified disorder of calcium metabolism,Unspecified disorder of calcium metabolism,Disorders of calcium metabolism,9
E84,0,E840,Cystic fibrosis with pulmonary manifestations,Cystic fibrosis with pulmonary manifestations,Cystic fibrosis,9
E85,0,E850,Non-neuropathic heredofamilial amyloidosis,Non-neuropathic heredofamilial amyloidosis,Amyloidosis,9
E86,0,E860,Dehydration,Dehydration,Volume depletion,9
E87,0,E870,Hyperosmolality and hypernatremia,Hyperosmolality and hypernatremia,"Other disorders of fluid, electrolyte and acid-base balance",9
E877,0,E8770,"Fluid overload, unspecified","Fluid overload, unspecified",Fluid overload,9
E884,0,E8840,"Mitochondrial metabolism disorder, unspecified","Mitochondrial metabolism disorder, unspecified",Mitochondrial metabolism disorders,9
E89,0,E890,Postprocedural hypothyroidism,Postprocedural hypothyroidism,"Postprocedural endocrine and metabolic complications and disorders, not elsewhere classified",9
E894,0,E8940,Asymptomatic postprocedural ovarian failure,Asymptomatic postprocedural ovarian failure,Postprocedural ovarian failure,9
E8981,0,E89810,Postproc hemor of an endo sys org fol an endo sys procedure,Postprocedural hemorrhage of an endocrine system organ or structure following an endocrine system procedure,Postprocedural hemorrhage of an endocrine system organ or structure following a procedure,9
E8982,0,E89820,Postproc hematoma of an endo sys org fol an endo sys proc,Postprocedural hematoma of an endocrine system organ or structure following an endocrine system procedure,Postprocedural hematoma and seroma of an endocrine system organ or structure,9
F015,0,F0150,Vascular dementia without behavioral disturbance,Vascular dementia without behavioral disturbance,Vascular dementia,9
F028,0,F0280,Dementia in oth diseases classd elswhr w/o behavrl disturb,Dementia in other diseases classified elsewhere without behavioral disturbance,Dementia in other diseases classified elsewhere,9
F039,0,F0390,Unspecified dementia without behavioral disturbance,Unspecified dementia without behavioral disturbance,Unspecified dementia,9
F06,0,F060,Psychotic disorder w hallucin due to known physiol condition,Psychotic disorder with hallucinations due to known physiological condition,Other mental disorders due to known physiological condition,9
F063,0,F0630,"Mood disorder due to known physiological condition, unsp","Mood disorder due to known physiological condition, unspecified",Mood disorder due to known physiological condition,9
F07,0,F070,Personality change due to known physiological condition,Personality change due to known physiological condition,Personality and behavioral disorders due to known physiological condition,9
F101,0,F1010,"Alcohol abuse, uncomplicated","Alcohol abuse, uncomplicated",Alcohol abuse,9
F1012,0,F10120,"Alcohol abuse with intoxication, uncomplicated","Alcohol abuse with intoxication, uncomplicated",Alcohol abuse with intoxication,9
F1015,0,F10150,Alcohol abuse w alcoh-induce psychotic disorder w delusions,Alcohol abuse with alcohol-induced psychotic disorder with delusions,Alcohol abuse with alcohol-induced psychotic disorder,9
F1018,0,F10180,Alcohol abuse with alcohol-induced anxiety disorder,Alcohol abuse with alcohol-induced anxiety disorder,Alcohol abuse with other alcohol-induced disorders,9
F102,0,F1020,"Alcohol dependence, uncomplicated","Alcohol dependence, uncomplicated",Alcohol dependence,9
F1022,0,F10220,"Alcohol dependence with intoxication, uncomplicated","Alcohol dependence with intoxication, uncomplicated",Alcohol dependence with intoxication,9
F1023,0,F10230,"Alcohol dependence with withdrawal, uncomplicated","Alcohol dependence with withdrawal, uncomplicated",Alcohol dependence with withdrawal,9
F1025,0,F10250,Alcohol depend w alcoh-induce psychotic disorder w delusions,Alcohol dependence with alcohol-induced psychotic disorder with delusions,Alcohol dependence with alcohol-induced psychotic disorder,9
F1028,0,F10280,Alcohol dependence with alcohol-induced anxiety disorder,Alcohol dependence with alcohol-induced anxiety disorder,Alcohol dependence with other alcohol-induced disorders,9
F1092,0,F10920,"Alcohol use, unspecified with intoxication, uncomplicated","Alcohol use, unspecified with intoxication, uncomplicated","Alcohol use, unspecified with intoxication",9
F1095,0,F10950,"Alcohol use, unsp w alcoh-induce psych disorder w delusions","Alcohol use, unspecified with alcohol-induced psychotic disorder with delusions","Alcohol use, unspecified with alcohol-induced psychotic disorder",9
F1098,0,F10980,"Alcohol use, unsp with alcohol-induced anxiety disorder","Alcohol use, unspecified with alcohol-induced anxiety disorder","Alcohol use, unspecified with other alcohol-induced disorders",9
F111,0,F1110,"Opioid abuse, uncomplicated","Opioid abuse, uncomplicated",Opioid abuse,9
F1112,0,F11120,"Opioid abuse with intoxication, uncomplicated","Opioid abuse with intoxication, uncomplicated",Opioid abuse with intoxication,9
F1115,0,F11150,Opioid abuse w opioid-induced psychotic disorder w delusions,Opioid abuse with opioid-induced psychotic disorder with delusions,Opioid abuse with opioid-induced psychotic disorder,9
F112,0,F1120,"Opioid dependence, uncomplicated","Opioid dependence, uncomplicated",Opioid dependence,9
F1122,0,F11220,"Opioid dependence with intoxication, uncomplicated","Opioid dependence with intoxication, uncomplicated",Opioid dependence with intoxication,9
F1125,0,F11250,Opioid depend w opioid-induc psychotic disorder w delusions,Opioid dependence with opioid-induced psychotic disorder with delusions,Opioid dependence with opioid-induced psychotic disorder,9
F119,0,F1190,"Opioid use, unspecified, uncomplicated","Opioid use, unspecified, uncomplicated","Opioid use, unspecified",9
F1192,0,F11920,"Opioid use, unspecified with intoxication, uncomplicated","Opioid use, unspecified with intoxication, uncomplicated","Opioid use, unspecified with intoxication",9
F1195,0,F11950,"Opioid use, unsp w opioid-induc psych disorder w delusions","Opioid use, unspecified with opioid-induced psychotic disorder with delusions","Opioid use, unspecified with opioid-induced psychotic disorder",9
F121,0,F1210,"Cannabis abuse, uncomplicated","Cannabis abuse, uncomplicated",Cannabis abuse,9
F1212,0,F12120,"Cannabis abuse with intoxication, uncomplicated","Cannabis abuse with intoxication, uncomplicated",Cannabis abuse with intoxication,9
F1215,0,F12150,Cannabis abuse with psychotic disorder with delusions,Cannabis abuse with psychotic disorder with delusions,Cannabis abuse with psychotic disorder,9
F1218,0,F12180,Cannabis abuse with cannabis-induced anxiety disorder,Cannabis abuse with cannabis-induced anxiety disorder,Cannabis abuse with other cannabis-induced disorder,9
F122,0,F1220,"Cannabis dependence, uncomplicated","Cannabis dependence, uncomplicated",Cannabis dependence,9
F1222,0,F12220,"Cannabis dependence with intoxication, uncomplicated","Cannabis dependence with intoxication, uncomplicated",Cannabis dependence with intoxication,9
F1225,0,F12250,Cannabis dependence with psychotic disorder with delusions,Cannabis dependence with psychotic disorder with delusions,Cannabis dependence with psychotic disorder,9
F1228,0,F12280,Cannabis dependence with cannabis-induced anxiety disorder,Cannabis dependence with cannabis-induced anxiety disorder,Cannabis dependence with other cannabis-induced disorder,9
F129,0,F1290,"Cannabis use, unspecified, uncomplicated","Cannabis use, unspecified, uncomplicated","Cannabis use, unspecified",9
F1292,0,F12920,"Cannabis use, unspecified with intoxication, uncomplicated","Cannabis use, unspecified with intoxication, uncomplicated","Cannabis use, unspecified with intoxication",9
F1295,0,F12950,"Cannabis use, unsp with psychotic disorder with delusions","Cannabis use, unspecified with psychotic disorder with delusions","Cannabis use, unspecified with psychotic disorder",9
F1298,0,F12980,"Cannabis use, unspecified with anxiety disorder","Cannabis use, unspecified with anxiety disorder","Cannabis use, unspecified with other cannabis-induced disorder",9
F131,0,F1310,"Sedative, hypnotic or anxiolytic abuse, uncomplicated","Sedative, hypnotic or anxiolytic abuse, uncomplicated","Sedative, hypnotic or anxiolytic-related abuse",9
F1312,0,F13120,"Sedatv/hyp/anxiolytc abuse w intoxication, uncomplicated","Sedative, hypnotic or anxiolytic abuse with intoxication, uncomplicated","Sedative, hypnotic or anxiolytic abuse with intoxication",9
F1315,0,F13150,Sedatv/hyp/anxiolytc abuse w psychotic disorder w delusions,"Sedative, hypnotic or anxiolytic abuse with sedative, hypnotic or anxiolytic-induced psychotic disorder with delusions","Sedative, hypnotic or anxiolytic abuse with sedative, hypnotic or anxiolytic-induced psychotic disorder",9
F1318,0,F13180,"Sedative, hypnotic or anxiolytic abuse w anxiety disorder","Sedative, hypnotic or anxiolytic abuse with sedative, hypnotic or anxiolytic-induced anxiety disorder","Sedative, hypnotic or anxiolytic abuse with other sedative, hypnotic or anxiolytic-induced disorders",9
F132,0,F1320,"Sedative, hypnotic or anxiolytic dependence, uncomplicated","Sedative, hypnotic or anxiolytic dependence, uncomplicated","Sedative, hypnotic or anxiolytic-related dependence",9
F1322,0,F13220,"Sedatv/hyp/anxiolytc dependence w intoxication, uncomp","Sedative, hypnotic or anxiolytic dependence with intoxication, uncomplicated","Sedative, hypnotic or anxiolytic dependence with intoxication",9
F1323,0,F13230,"Sedatv/hyp/anxiolytc dependence w withdrawal, uncomplicated","Sedative, hypnotic or anxiolytic dependence with withdrawal, uncomplicated","Sedative, hypnotic or anxiolytic dependence with withdrawal",9
F1325,0,F13250,Sedatv/hyp/anxiolytc depend w psychotic disorder w delusions,"Sedative, hypnotic or anxiolytic dependence with sedative, hypnotic or anxiolytic-induced psychotic disorder with delusions","Sedative, hypnotic or anxiolytic dependence with sedative, hypnotic or anxiolytic-induced psychotic disorder",9
F1328,0,F13280,Sedatv/hyp/anxiolytc dependence w anxiety disorder,"Sedative, hypnotic or anxiolytic dependence with sedative, hypnotic or anxiolytic-induced anxiety disorder","Sedative, hypnotic or anxiolytic dependence with other sedative, hypnotic or anxiolytic-induced disorders",9
F139,0,F1390,"Sedative, hypnotic, or anxiolytic use, unsp, uncomplicated","Sedative, hypnotic, or anxiolytic use, unspecified, uncomplicated","Sedative, hypnotic or anxiolytic-related use, unspecified",9
F1392,0,F13920,"Sedatv/hyp/anxiolytc use, unsp w intoxication, uncomplicated","Sedative, hypnotic or anxiolytic use, unspecified with intoxication, uncomplicated","Sedative, hypnotic or anxiolytic use, unspecified with intoxication",9
F1393,0,F13930,"Sedatv/hyp/anxiolytc use, unsp w withdrawal, uncomplicated","Sedative, hypnotic or anxiolytic use, unspecified with withdrawal, uncomplicated","Sedative, hypnotic or anxiolytic use, unspecified with withdrawal",9
F1395,0,F13950,"Sedatv/hyp/anxiolytc use, unsp w psych disorder w delusions","Sedative, hypnotic or anxiolytic use, unspecified with sedative, hypnotic or anxiolytic-induced psychotic disorder with delusions","Sedative, hypnotic or anxiolytic use, unspecified with sedative, hypnotic or anxiolytic-induced psychotic disorder",9
F1398,0,F13980,"Sedatv/hyp/anxiolytc use, unsp w anxiety disorder","Sedative, hypnotic or anxiolytic use, unspecified with sedative, hypnotic or anxiolytic-induced anxiety disorder","Sedative, hypnotic or anxiolytic use, unspecified with other sedative, hypnotic or anxiolytic-induced disorders",9
F141,0,F1410,"Cocaine abuse, uncomplicated","Cocaine abuse, uncomplicated",Cocaine abuse,9
F1412,0,F14120,"Cocaine abuse with intoxication, uncomplicated","Cocaine abuse with intoxication, uncomplicated",Cocaine abuse with intoxication,9
F1415,0,F14150,Cocaine abuse w cocaine-induc psychotic disorder w delusions,Cocaine abuse with cocaine-induced psychotic disorder with delusions,Cocaine abuse with cocaine-induced psychotic disorder,9
F1418,0,F14180,Cocaine abuse with cocaine-induced anxiety disorder,Cocaine abuse with cocaine-induced anxiety disorder,Cocaine abuse with other cocaine-induced disorder,9
F142,0,F1420,"Cocaine dependence, uncomplicated","Cocaine dependence, uncomplicated",Cocaine dependence,9
F1422,0,F14220,"Cocaine dependence with intoxication, uncomplicated","Cocaine dependence with intoxication, uncomplicated",Cocaine dependence with intoxication,9
F1425,0,F14250,Cocaine depend w cocaine-induc psych disorder w delusions,Cocaine dependence with cocaine-induced psychotic disorder with delusions,Cocaine dependence with cocaine-induced psychotic disorder,9
F1428,0,F14280,Cocaine dependence with cocaine-induced anxiety disorder,Cocaine dependence with cocaine-induced anxiety disorder,Cocaine dependence with other cocaine-induced disorder,9
F149,0,F1490,"Cocaine use, unspecified, uncomplicated","Cocaine use, unspecified, uncomplicated","Cocaine use, unspecified",9
F1492,0,F14920,"Cocaine use, unspecified with intoxication, uncomplicated","Cocaine use, unspecified with intoxication, uncomplicated","Cocaine use, unspecified with intoxication",9
F1495,0,F14950,"Cocaine use, unsp w cocaine-induc psych disorder w delusions","Cocaine use, unspecified with cocaine-induced psychotic disorder with delusions","Cocaine use, unspecified with cocaine-induced psychotic disorder",9
F1498,0,F14980,"Cocaine use, unsp with cocaine-induced anxiety disorder","Cocaine use, unspecified with cocaine-induced anxiety disorder","Cocaine use, unspecified with other specified cocaine-induced disorder",9
F151,0,F1510,"Other stimulant abuse, uncomplicated","Other stimulant abuse, uncomplicated",Other stimulant abuse,9
F1512,0,F15120,"Other stimulant abuse with intoxication, uncomplicated","Other stimulant abuse with intoxication, uncomplicated",Other stimulant abuse with intoxication,9
F1515,0,F15150,Oth stimulant abuse w stim-induce psych disorder w delusions,Other stimulant abuse with stimulant-induced psychotic disorder with delusions,Other stimulant abuse with stimulant-induced psychotic disorder,9
F1518,0,F15180,Oth stimulant abuse with stimulant-induced anxiety disorder,Other stimulant abuse with stimulant-induced anxiety disorder,Other stimulant abuse with other stimulant-induced disorder,9
F152,0,F1520,"Other stimulant dependence, uncomplicated","Other stimulant dependence, uncomplicated",Other stimulant dependence,9
F1522,0,F15220,"Other stimulant dependence with intoxication, uncomplicated","Other stimulant dependence with intoxication, uncomplicated",Other stimulant dependence with intoxication,9
F1525,0,F15250,Oth stim depend w stim-induce psych disorder w delusions,Other stimulant dependence with stimulant-induced psychotic disorder with delusions,Other stimulant dependence with stimulant-induced psychotic disorder,9
F1528,0,F15280,Oth stimulant dependence w stim-induce anxiety disorder,Other stimulant dependence with stimulant-induced anxiety disorder,Other stimulant dependence with other stimulant-induced disorder,9
F159,0,F1590,"Other stimulant use, unspecified, uncomplicated","Other stimulant use, unspecified, uncomplicated","Other stimulant use, unspecified",9
F1592,0,F15920,"Other stimulant use, unsp with intoxication, uncomplicated","Other stimulant use, unspecified with intoxication, uncomplicated","Other stimulant use, unspecified with intoxication",9
F1595,0,F15950,"Oth stim use, unsp w stim-induce psych disorder w delusions","Other stimulant use, unspecified with stimulant-induced psychotic disorder with delusions","Other stimulant use, unspecified with stimulant-induced psychotic disorder",9
F1598,0,F15980,"Oth stimulant use, unsp w stimulant-induced anxiety disorder","Other stimulant use, unspecified with stimulant-induced anxiety disorder","Other stimulant use, unspecified with other stimulant-induced disorder",9
F161,0,F1610,"Hallucinogen abuse, uncomplicated","Hallucinogen abuse, uncomplicated",Hallucinogen abuse,9
F1612,0,F16120,"Hallucinogen abuse with intoxication, uncomplicated","Hallucinogen abuse with intoxication, uncomplicated",Hallucinogen abuse with intoxication,9
F1615,0,F16150,Hallucinogen abuse w psychotic disorder w delusions,Hallucinogen abuse with hallucinogen-induced psychotic disorder with delusions,Hallucinogen abuse with hallucinogen-induced psychotic disorder,9
F1618,0,F16180,Hallucinogen abuse w hallucinogen-induced anxiety disorder,Hallucinogen abuse with hallucinogen-induced anxiety disorder,Hallucinogen abuse with other hallucinogen-induced disorder,9
F162,0,F1620,"Hallucinogen dependence, uncomplicated","Hallucinogen dependence, uncomplicated",Hallucinogen dependence,9
F1622,0,F16220,"Hallucinogen dependence with intoxication, uncomplicated","Hallucinogen dependence with intoxication, uncomplicated",Hallucinogen dependence with intoxication,9
F1625,0,F16250,Hallucinogen dependence w psychotic disorder w delusions,Hallucinogen dependence with hallucinogen-induced psychotic disorder with delusions,Hallucinogen dependence with hallucinogen-induced psychotic disorder,9
F1628,0,F16280,Hallucinogen dependence w anxiety disorder,Hallucinogen dependence with hallucinogen-induced anxiety disorder,Hallucinogen dependence with other hallucinogen-induced disorder,9
F169,0,F1690,"Hallucinogen use, unspecified, uncomplicated","Hallucinogen use, unspecified, uncomplicated","Hallucinogen use, unspecified",9
F1692,0,F16920,"Hallucinogen use, unsp with intoxication, uncomplicated","Hallucinogen use, unspecified with intoxication, uncomplicated","Hallucinogen use, unspecified with intoxication",9
F1695,0,F16950,"Hallucinogen use, unsp w psychotic disorder w delusions","Hallucinogen use, unspecified with hallucinogen-induced psychotic disorder with delusions","Hallucinogen use, unspecified with hallucinogen-induced psychotic disorder",9
F1698,0,F16980,"Hallucinogen use, unsp w anxiety disorder","Hallucinogen use, unspecified with hallucinogen-induced anxiety disorder","Hallucinogen use, unspecified with other specified hallucinogen-induced disorder",9
F1720,0,F17200,"Nicotine dependence, unspecified, uncomplicated","Nicotine dependence, unspecified, uncomplicated","Nicotine dependence, unspecified",9
F1721,0,F17210,"Nicotine dependence, cigarettes, uncomplicated","Nicotine dependence, cigarettes, uncomplicated","Nicotine dependence, cigarettes",9
F1722,0,F17220,"Nicotine dependence, chewing tobacco, uncomplicated","Nicotine dependence, chewing tobacco, uncomplicated","Nicotine dependence, chewing tobacco",9
F1729,0,F17290,"Nicotine dependence, other tobacco product, uncomplicated","Nicotine dependence, other tobacco product, uncomplicated","Nicotine dependence, other tobacco product",9
F181,0,F1810,"Inhalant abuse, uncomplicated","Inhalant abuse, uncomplicated",Inhalant abuse,9
F1812,0,F18120,"Inhalant abuse with intoxication, uncomplicated","Inhalant abuse with intoxication, uncomplicated",Inhalant abuse with intoxication,9
F1815,0,F18150,Inhalant abuse w inhalnt-induce psych disorder w delusions,Inhalant abuse with inhalant-induced psychotic disorder with delusions,Inhalant abuse with inhalant-induced psychotic disorder,9
F1818,0,F18180,Inhalant abuse with inhalant-induced anxiety disorder,Inhalant abuse with inhalant-induced anxiety disorder,Inhalant abuse with other inhalant-induced disorders,9
F182,0,F1820,"Inhalant dependence, uncomplicated","Inhalant dependence, uncomplicated",Inhalant dependence,9
F1822,0,F18220,"Inhalant dependence with intoxication, uncomplicated","Inhalant dependence with intoxication, uncomplicated",Inhalant dependence with intoxication,9
F1825,0,F18250,Inhalant depend w inhalnt-induce psych disorder w delusions,Inhalant dependence with inhalant-induced psychotic disorder with delusions,Inhalant dependence with inhalant-induced psychotic disorder,9
F1828,0,F18280,Inhalant dependence with inhalant-induced anxiety disorder,Inhalant dependence with inhalant-induced anxiety disorder,Inhalant dependence with other inhalant-induced disorders,9
F189,0,F1890,"Inhalant use, unspecified, uncomplicated","Inhalant use, unspecified, uncomplicated","Inhalant use, unspecified",9
F1892,0,F18920,"Inhalant use, unspecified with intoxication, uncomplicated","Inhalant use, unspecified with intoxication, uncomplicated","Inhalant use, unspecified with intoxication",9
F1895,0,F18950,"Inhalant use, unsp w inhalnt-induce psych disord w delusions","Inhalant use, unspecified with inhalant-induced psychotic disorder with delusions","Inhalant use, unspecified with inhalant-induced psychotic disorder",9
F1898,0,F18980,"Inhalant use, unsp with inhalant-induced anxiety disorder","Inhalant use, unspecified with inhalant-induced anxiety disorder","Inhalant use, unspecified with other inhalant-induced disorders",9
F191,0,F1910,"Other psychoactive substance abuse, uncomplicated","Other psychoactive substance abuse, uncomplicated",Other psychoactive substance abuse,9
F1912,0,F19120,"Oth psychoactive substance abuse w intoxication, uncomp","Other psychoactive substance abuse with intoxication, uncomplicated",Other psychoactive substance abuse with intoxication,9
F1915,0,F19150,Oth psychoactv substance abuse w psych disorder w delusions,Other psychoactive substance abuse with psychoactive substance-induced psychotic disorder with delusions,Other psychoactive substance abuse with psychoactive substance-induced psychotic disorder,9
F1918,0,F19180,Oth psychoactive substance abuse w anxiety disorder,Other psychoactive substance abuse with psychoactive substance-induced anxiety disorder,Other psychoactive substance abuse with other psychoactive substance-induced disorders,9
F192,0,F1920,"Other psychoactive substance dependence, uncomplicated","Other psychoactive substance dependence, uncomplicated",Other psychoactive substance dependence,9
F1922,0,F19220,"Oth psychoactive substance dependence w intoxication, uncomp","Other psychoactive substance dependence with intoxication, uncomplicated",Other psychoactive substance dependence with intoxication,9
F1923,0,F19230,"Oth psychoactive substance dependence w withdrawal, uncomp","Other psychoactive substance dependence with withdrawal, uncomplicated",Other psychoactive substance dependence with withdrawal,9
F1925,0,F19250,Oth psychoactv substance depend w psych disorder w delusions,Other psychoactive substance dependence with psychoactive substance-induced psychotic disorder with delusions,Other psychoactive substance dependence with psychoactive substance-induced psychotic disorder,9
F1928,0,F19280,Oth psychoactive substance dependence w anxiety disorder,Other psychoactive substance dependence with psychoactive substance-induced anxiety disorder,Other psychoactive substance dependence with other psychoactive substance-induced disorders,9
B05,1,B051,Measles complicated by meningitis,Measles complicated by meningitis,Measles,9
F199,0,F1990,"Other psychoactive substance use, unspecified, uncomplicated","Other psychoactive substance use, unspecified, uncomplicated","Other psychoactive substance use, unspecified",9
F1992,0,F19920,"Oth psychoactive substance use, unsp w intoxication, uncomp","Other psychoactive substance use, unspecified with intoxication, uncomplicated","Other psychoactive substance use, unspecified with intoxication",9
F1993,0,F19930,"Oth psychoactive substance use, unsp w withdrawal, uncomp","Other psychoactive substance use, unspecified with withdrawal, uncomplicated","Other psychoactive substance use, unspecified with withdrawal",9
F1995,0,F19950,"Oth psychoactv sub use, unsp w psych disorder w delusions","Other psychoactive substance use, unspecified with psychoactive substance-induced psychotic disorder with delusions","Other psychoactive substance use, unspecified with psychoactive substance-induced psychotic disorder",9
F1998,0,F19980,"Oth psychoactive substance use, unsp w anxiety disorder","Other psychoactive substance use, unspecified with psychoactive substance-induced anxiety disorder","Other psychoactive substance use, unspecified with other psychoactive substance-induced disorders",9
F20,0,F200,Paranoid schizophrenia,Paranoid schizophrenia,Schizophrenia,9
F25,0,F250,"Schizoaffective disorder, bipolar type","Schizoaffective disorder, bipolar type",Schizoaffective disorders,9
F301,0,F3010,"Manic episode without psychotic symptoms, unspecified","Manic episode without psychotic symptoms, unspecified",Manic episode without psychotic symptoms,9
F31,0,F310,"Bipolar disorder, current episode hypomanic","Bipolar disorder, current episode hypomanic",Bipolar disorder,9
F311,0,F3110,"Bipolar disord, crnt episode manic w/o psych features, unsp","Bipolar disorder, current episode manic without psychotic features, unspecified","Bipolar disorder, current episode manic without psychotic features",9
F313,0,F3130,"Bipolar disord, crnt epsd depress, mild or mod severt, unsp","Bipolar disorder, current episode depressed, mild or moderate severity, unspecified","Bipolar disorder, current episode depressed, mild or moderate severity",9
F316,0,F3160,"Bipolar disorder, current episode mixed, unspecified","Bipolar disorder, current episode mixed, unspecified","Bipolar disorder, current episode mixed",9
F317,0,F3170,"Bipolar disord, currently in remis, most recent episode unsp","Bipolar disorder, currently in remission, most recent episode unspecified","Bipolar disorder, currently in remission",9
F32,0,F320,"Major depressive disorder, single episode, mild","Major depressive disorder, single episode, mild","Major depressive disorder, single episode",9
F33,0,F330,"Major depressive disorder, recurrent, mild","Major depressive disorder, recurrent, mild","Major depressive disorder, recurrent",9
F334,0,F3340,"Major depressive disorder, recurrent, in remission, unsp","Major depressive disorder, recurrent, in remission, unspecified","Major depressive disorder, recurrent, in remission",9
F34,0,F340,Cyclothymic disorder,Cyclothymic disorder,Persistent mood [affective] disorders,9
F400,0,F4000,"Agoraphobia, unspecified","Agoraphobia, unspecified",Agoraphobia,9
F401,0,F4010,"Social phobia, unspecified","Social phobia, unspecified",Social phobias,9
F4021,0,F40210,Arachnophobia,Arachnophobia,Animal type phobia,9
F4022,0,F40220,Fear of thunderstorms,Fear of thunderstorms,Natural environment type phobia,9
F4023,0,F40230,Fear of blood,Fear of blood,"Blood, injection, injury type phobia",9
F4024,0,F40240,Claustrophobia,Claustrophobia,Situational type phobia,9
F4029,0,F40290,Androphobia,Androphobia,Other specified phobia,9
F41,0,F410,Panic disorder [episodic paroxysmal anxiety],Panic disorder [episodic paroxysmal anxiety],Other anxiety disorders,9
F43,0,F430,Acute stress reaction,Acute stress reaction,"Reaction to severe stress, and adjustment disorders",9
F431,0,F4310,"Post-traumatic stress disorder, unspecified","Post-traumatic stress disorder, unspecified",Post-traumatic stress disorder (PTSD),9
F432,0,F4320,"Adjustment disorder, unspecified","Adjustment disorder, unspecified",Adjustment disorders,9
F44,0,F440,Dissociative amnesia,Dissociative amnesia,Dissociative and conversion disorders,9
F45,0,F450,Somatization disorder,Somatization disorder,Somatoform disorders,9
F452,0,F4520,"Hypochondriacal disorder, unspecified","Hypochondriacal disorder, unspecified",Hypochondriacal disorders,9
F500,0,F5000,"Anorexia nervosa, unspecified","Anorexia nervosa, unspecified",Anorexia nervosa,9
F52,0,F520,Hypoactive sexual desire disorder,Hypoactive sexual desire disorder,Sexual dysfunction not due to a substance or known physiological condition,9
F55,0,F550,Abuse of antacids,Abuse of antacids,Abuse of non-psychoactive substances,9
F60,0,F600,Paranoid personality disorder,Paranoid personality disorder,Specific personality disorders,9
F63,0,F630,Pathological gambling,Pathological gambling,Impulse disorders,9
F64,0,F640,Transsexualism,Transsexualism,Gender identity disorders,9
F65,0,F650,Fetishism,Fetishism,Paraphilias,9
F655,0,F6550,"Sadomasochism, unspecified","Sadomasochism, unspecified",Sadomasochism,9
F681,0,F6810,"Factitious disorder, unspecified","Factitious disorder, unspecified",Factitious disorder,9
F80,0,F800,Phonological disorder,Phonological disorder,Specific developmental disorders of speech and language,9
F81,0,F810,Specific reading disorder,Specific reading disorder,Specific developmental disorders of scholastic skills,9
F84,0,F840,Autistic disorder,Autistic disorder,Pervasive developmental disorders,9
F90,0,F900,"Attn-defct hyperactivity disorder, predom inattentive type","Attention-deficit hyperactivity disorder, predominantly inattentive type",Attention-deficit hyperactivity disorders,9
F91,0,F910,Conduct disorder confined to family context,Conduct disorder confined to family context,Conduct disorders,9
F93,0,F930,Separation anxiety disorder of childhood,Separation anxiety disorder of childhood,Emotional disorders with onset specific to childhood,9
F94,0,F940,Selective mutism,Selective mutism,Disorders of social functioning with onset specific to childhood and adolescence,9
F95,0,F950,Transient tic disorder,Transient tic disorder,Tic disorder,9
G575,0,G5750,"Tarsal tunnel syndrome, unspecified lower limb","Tarsal tunnel syndrome, unspecified lower limb",Tarsal tunnel syndrome,9
F98,0,F980,Enuresis not due to a substance or known physiol condition,Enuresis not due to a substance or known physiological condition,Other behavioral and emotional disorders with onset usually occurring in childhood and adolescence,9
G00,0,G000,Hemophilus meningitis,Hemophilus meningitis,"Bacterial meningitis, not elsewhere classified",9
G03,0,G030,Nonpyogenic meningitis,Nonpyogenic meningitis,Meningitis due to other and unspecified causes,9
G040,0,G0400,"Acute disseminated encephalitis and encephalomyelitis, unsp","Acute disseminated encephalitis and encephalomyelitis, unspecified",Acute disseminated encephalitis and encephalomyelitis (ADEM),9
G043,0,G0430,"Acute necrotizing hemorrhagic encephalopathy, unspecified","Acute necrotizing hemorrhagic encephalopathy, unspecified",Acute necrotizing hemorrhagic encephalopathy,9
G049,0,G0490,"Encephalitis and encephalomyelitis, unspecified","Encephalitis and encephalomyelitis, unspecified","Encephalitis, myelitis and encephalomyelitis, unspecified",9
G06,0,G060,Intracranial abscess and granuloma,Intracranial abscess and granuloma,Intracranial and intraspinal abscess and granuloma,9
G11,0,G110,Congenital nonprogressive ataxia,Congenital nonprogressive ataxia,Hereditary ataxia,9
G12,0,G120,"Infantile spinal muscular atrophy, type I [Werdnig-Hoffman]","Infantile spinal muscular atrophy, type I [Werdnig-Hoffman]",Spinal muscular atrophy and related syndromes,9
G122,0,G1220,"Motor neuron disease, unspecified","Motor neuron disease, unspecified",Motor neuron disease,9
G13,0,G130,Paraneoplastic neuromyopathy and neuropathy,Paraneoplastic neuromyopathy and neuropathy,Systemic atrophies primarily affecting central nervous system in diseases classified elsewhere,9
G21,0,G210,Malignant neuroleptic syndrome,Malignant neuroleptic syndrome,Secondary parkinsonism,9
G23,0,G230,Hallervorden-Spatz disease,Hallervorden-Spatz disease,Other degenerative diseases of basal ganglia,9
G25,0,G250,Essential tremor,Essential tremor,Other extrapyramidal and movement disorders,9
G257,0,G2570,"Drug induced movement disorder, unspecified","Drug induced movement disorder, unspecified",Other and unspecified drug induced movement disorders,9
G30,0,G300,Alzheimer's disease with early onset,Alzheimer's disease with early onset,Alzheimer's disease,9
G32,0,G320,Subac comb degeneration of spinal cord in dis classd elswhr,Subacute combined degeneration of spinal cord in diseases classified elsewhere,Other degenerative disorders of nervous system in diseases classified elsewhere,9
G36,0,G360,Neuromyelitis optica [Devic],Neuromyelitis optica [Devic],Other acute disseminated demyelination,9
G37,0,G370,Diffuse sclerosis of central nervous system,Diffuse sclerosis of central nervous system,Other demyelinating diseases of central nervous system,9
G43A,0,G43A0,"Cyclical vomiting, not intractable","Cyclical vomiting, not intractable",Cyclical vomiting,9
G43B,0,G43B0,"Ophthalmoplegic migraine, not intractable","Ophthalmoplegic migraine, not intractable",Ophthalmoplegic migraine,9
G43C,0,G43C0,"Periodic headache syndromes in chld/adlt, not intractable","Periodic headache syndromes in child or adult, not intractable",Periodic headache syndromes in child or adult,9
G43D,0,G43D0,"Abdominal migraine, not intractable","Abdominal migraine, not intractable",Abdominal migraine,9
G444,0,G4440,"Drug-induced headache, NEC, not intractable","Drug-induced headache, not elsewhere classified, not intractable","Drug-induced headache, not elsewhere classified",9
G45,0,G450,Vertebro-basilar artery syndrome,Vertebro-basilar artery syndrome,Transient cerebral ischemic attacks and related syndromes,9
G46,0,G460,Middle cerebral artery syndrome,Middle cerebral artery syndrome,Vascular syndromes of brain in cerebrovascular diseases,9
G470,0,G4700,"Insomnia, unspecified","Insomnia, unspecified",Insomnia,9
G471,0,G4710,"Hypersomnia, unspecified","Hypersomnia, unspecified",Hypersomnia,9
G472,0,G4720,"Circadian rhythm sleep disorder, unspecified type","Circadian rhythm sleep disorder, unspecified type",Circadian rhythm sleep disorders,9
G473,0,G4730,"Sleep apnea, unspecified","Sleep apnea, unspecified",Sleep apnea,9
G475,0,G4750,"Parasomnia, unspecified","Parasomnia, unspecified",Parasomnia,9
G50,0,G500,Trigeminal neuralgia,Trigeminal neuralgia,Disorders of trigeminal nerve,9
G51,0,G510,Bell's palsy,Bell's palsy,Facial nerve disorders,9
G52,0,G520,Disorders of olfactory nerve,Disorders of olfactory nerve,Disorders of other cranial nerves,9
G54,0,G540,Brachial plexus disorders,Brachial plexus disorders,Nerve root and plexus disorders,9
G560,0,G5600,"Carpal tunnel syndrome, unspecified upper limb","Carpal tunnel syndrome, unspecified upper limb",Carpal tunnel syndrome,9
G561,0,G5610,"Other lesions of median nerve, unspecified upper limb","Other lesions of median nerve, unspecified upper limb",Other lesions of median nerve,9
G562,0,G5620,"Lesion of ulnar nerve, unspecified upper limb","Lesion of ulnar nerve, unspecified upper limb",Lesion of ulnar nerve,9
G563,0,G5630,"Lesion of radial nerve, unspecified upper limb","Lesion of radial nerve, unspecified upper limb",Lesion of radial nerve,9
G564,0,G5640,Causalgia of unspecified upper limb,Causalgia of unspecified upper limb,Causalgia of upper limb,9
G568,0,G5680,Other specified mononeuropathies of unspecified upper limb,Other specified mononeuropathies of unspecified upper limb,Other specified mononeuropathies of upper limb,9
G569,0,G5690,Unspecified mononeuropathy of unspecified upper limb,Unspecified mononeuropathy of unspecified upper limb,Unspecified mononeuropathy of upper limb,9
G570,0,G5700,"Lesion of sciatic nerve, unspecified lower limb","Lesion of sciatic nerve, unspecified lower limb",Lesion of sciatic nerve,9
G571,0,G5710,"Meralgia paresthetica, unspecified lower limb","Meralgia paresthetica, unspecified lower limb",Meralgia paresthetica,9
G572,0,G5720,"Lesion of femoral nerve, unspecified lower limb","Lesion of femoral nerve, unspecified lower limb",Lesion of femoral nerve,9
G573,0,G5730,"Lesion of lateral popliteal nerve, unspecified lower limb","Lesion of lateral popliteal nerve, unspecified lower limb",Lesion of lateral popliteal nerve,9
G574,0,G5740,"Lesion of medial popliteal nerve, unspecified lower limb","Lesion of medial popliteal nerve, unspecified lower limb",Lesion of medial popliteal nerve,9
A485,1,A4851,Infant botulism,Infant botulism,Other specified botulism,9
G576,0,G5760,"Lesion of plantar nerve, unspecified lower limb","Lesion of plantar nerve, unspecified lower limb",Lesion of plantar nerve,9
G577,0,G5770,Causalgia of unspecified lower limb,Causalgia of unspecified lower limb,Causalgia of lower limb,9
G578,0,G5780,Other specified mononeuropathies of unspecified lower limb,Other specified mononeuropathies of unspecified lower limb,Other specified mononeuropathies of lower limb,9
A00,1,A001,"Cholera due to Vibrio cholerae 01, biovar eltor","Cholera due to Vibrio cholerae 01, biovar eltor",Cholera,9
A010,1,A0101,Typhoid meningitis,Typhoid meningitis,Typhoid fever,9
A02,1,A021,Salmonella sepsis,Salmonella sepsis,Other salmonella infections,9
A022,1,A0221,Salmonella meningitis,Salmonella meningitis,Localized salmonella infections,9
A03,1,A031,Shigellosis due to Shigella flexneri,Shigellosis due to Shigella flexneri,Shigellosis,9
A04,1,A041,Enterotoxigenic Escherichia coli infection,Enterotoxigenic Escherichia coli infection,Other bacterial intestinal infections,9
A047,1,A0471,"Enterocolitis due to Clostridium difficile, recurrent","Enterocolitis due to Clostridium difficile, recurrent",Enterocolitis due to Clostridium difficile,9
A05,1,A051,Botulism food poisoning,Botulism food poisoning,"Other bacterial foodborne intoxications, not elsewhere classified",9
A06,1,A061,Chronic intestinal amebiasis,Chronic intestinal amebiasis,Amebiasis,9
A068,1,A0681,Amebic cystitis,Amebic cystitis,Amebic infection of other sites,9
A07,1,A071,Giardiasis [lambliasis],Giardiasis [lambliasis],Other protozoal intestinal diseases,9
A081,1,A0811,Acute gastroenteropathy due to Norwalk agent,Acute gastroenteropathy due to Norwalk agent,Acute gastroenteropathy due to Norwalk agent and other small round viruses,9
A083,1,A0831,Calicivirus enteritis,Calicivirus enteritis,Other viral enteritis,9
A17,1,A171,Meningeal tuberculoma,Meningeal tuberculoma,Tuberculosis of nervous system,9
A178,1,A1781,Tuberculoma of brain and spinal cord,Tuberculoma of brain and spinal cord,Other tuberculosis of nervous system,9
A180,1,A1801,Tuberculosis of spine,Tuberculosis of spine,Tuberculosis of bones and joints,9
A181,1,A1811,Tuberculosis of kidney and ureter,Tuberculosis of kidney and ureter,Tuberculosis of genitourinary system,9
A183,1,A1831,Tuberculous peritonitis,Tuberculous peritonitis,"Tuberculosis of intestines, peritoneum and mesenteric glands",9
A185,1,A1851,Tuberculous episcleritis,Tuberculous episcleritis,Tuberculosis of eye,9
A188,1,A1881,Tuberculosis of thyroid gland,Tuberculosis of thyroid gland,Tuberculosis of other specified organs,9
A19,1,A191,Acute miliary tuberculosis of multiple sites,Acute miliary tuberculosis of multiple sites,Miliary tuberculosis,9
A20,1,A201,Cellulocutaneous plague,Cellulocutaneous plague,Plague,9
A21,1,A211,Oculoglandular tularemia,Oculoglandular tularemia,Tularemia,9
A22,1,A221,Pulmonary anthrax,Pulmonary anthrax,Anthrax,9
A23,1,A231,Brucellosis due to Brucella abortus,Brucellosis due to Brucella abortus,Brucellosis,9
A24,1,A241,Acute and fulminating melioidosis,Acute and fulminating melioidosis,Glanders and melioidosis,9
A25,1,A251,Streptobacillosis,Streptobacillosis,Rat-bite fevers,9
A278,1,A2781,Aseptic meningitis in leptospirosis,Aseptic meningitis in leptospirosis,Other forms of leptospirosis,9
A28,1,A281,Cat-scratch disease,Cat-scratch disease,"Other zoonotic bacterial diseases, not elsewhere classified",9
A30,1,A301,Tuberculoid leprosy,Tuberculoid leprosy,Leprosy [Hansen's disease],9
A31,1,A311,Cutaneous mycobacterial infection,Cutaneous mycobacterial infection,Infection due to other mycobacteria,9
A321,1,A3211,Listerial meningitis,Listerial meningitis,Listerial meningitis and meningoencephalitis,9
A328,1,A3281,Oculoglandular listeriosis,Oculoglandular listeriosis,Other forms of listeriosis,9
A36,1,A361,Nasopharyngeal diphtheria,Nasopharyngeal diphtheria,Diphtheria,9
A368,1,A3681,Diphtheritic cardiomyopathy,Diphtheritic cardiomyopathy,Other diphtheria,9
A370,1,A3701,Whooping cough due to Bordetella pertussis with pneumonia,Whooping cough due to Bordetella pertussis with pneumonia,Whooping cough due to Bordetella pertussis,9
A371,1,A3711,Whooping cough due to Bordetella parapertussis w pneumonia,Whooping cough due to Bordetella parapertussis with pneumonia,Whooping cough due to Bordetella parapertussis,9
A378,1,A3781,Whooping cough due to oth Bordetella species with pneumonia,Whooping cough due to other Bordetella species with pneumonia,Whooping cough due to other Bordetella species,9
A379,1,A3791,"Whooping cough, unspecified species with pneumonia","Whooping cough, unspecified species with pneumonia","Whooping cough, unspecified species",9
A38,1,A381,Scarlet fever with myocarditis,Scarlet fever with myocarditis,Scarlet fever,9
A39,1,A391,Waterhouse-Friderichsen syndrome,Waterhouse-Friderichsen syndrome,Meningococcal infection,9
A395,1,A3951,Meningococcal endocarditis,Meningococcal endocarditis,Meningococcal heart disease,9
A398,1,A3981,Meningococcal encephalitis,Meningococcal encephalitis,Other meningococcal infections,9
A40,1,A401,"Sepsis due to streptococcus, group B","Sepsis due to streptococcus, group B",Streptococcal sepsis,9
A410,1,A4101,Sepsis due to Methicillin susceptible Staphylococcus aureus,Sepsis due to Methicillin susceptible Staphylococcus aureus,Sepsis due to Staphylococcus aureus,9
A415,1,A4151,Sepsis due to Escherichia coli [E. coli],Sepsis due to Escherichia coli [E. coli],Sepsis due to other Gram-negative organisms,9
A418,1,A4181,Sepsis due to Enterococcus,Sepsis due to Enterococcus,Other specified sepsis,9
A42,1,A421,Abdominal actinomycosis,Abdominal actinomycosis,Actinomycosis,9
A428,1,A4281,Actinomycotic meningitis,Actinomycotic meningitis,Other forms of actinomycosis,9
A43,1,A431,Cutaneous nocardiosis,Cutaneous nocardiosis,Nocardiosis,9
A44,1,A441,Cutaneous and mucocutaneous bartonellosis,Cutaneous and mucocutaneous bartonellosis,Bartonellosis,9
A48,1,A481,Legionnaires' disease,Legionnaires' disease,"Other bacterial diseases, not elsewhere classified",9
A490,1,A4901,"Methicillin suscep staph infection, unsp site","Methicillin susceptible Staphylococcus aureus infection, unspecified site","Staphylococcal infection, unspecified site",9
A500,1,A5001,Early congenital syphilitic oculopathy,Early congenital syphilitic oculopathy,"Early congenital syphilis, symptomatic",9
A503,1,A5031,Late congenital syphilitic interstitial keratitis,Late congenital syphilitic interstitial keratitis,Late congenital syphilitic oculopathy,9
A504,1,A5041,Late congenital syphilitic meningitis,Late congenital syphilitic meningitis,Late congenital neurosyphilis [juvenile neurosyphilis],9
A505,1,A5051,Clutton's joints,Clutton's joints,"Other late congenital syphilis, symptomatic",9
A51,1,A511,Primary anal syphilis,Primary anal syphilis,Early syphilis,9
A513,1,A5131,Condyloma latum,Condyloma latum,Secondary syphilis of skin and mucous membranes,9
A514,1,A5141,Secondary syphilitic meningitis,Secondary syphilitic meningitis,Other secondary syphilis,9
A520,1,A5201,Syphilitic aneurysm of aorta,Syphilitic aneurysm of aorta,Cardiovascular and cerebrovascular syphilis,9
A521,1,A5211,Tabes dorsalis,Tabes dorsalis,Symptomatic neurosyphilis,9
A527,1,A5271,Late syphilitic oculopathy,Late syphilitic oculopathy,Other symptomatic late syphilis,9
A540,1,A5401,"Gonococcal cystitis and urethritis, unspecified","Gonococcal cystitis and urethritis, unspecified",Gonococcal infection of lower genitourinary tract without periurethral or accessory gland abscess,9
A542,1,A5421,Gonococcal infection of kidney and ureter,Gonococcal infection of kidney and ureter,Gonococcal pelviperitonitis and other gonococcal genitourinary infection,9
A543,1,A5431,Gonococcal conjunctivitis,Gonococcal conjunctivitis,Gonococcal infection of eye,9
A544,1,A5441,Gonococcal spondylopathy,Gonococcal spondylopathy,Gonococcal infection of musculoskeletal system,9
A548,1,A5481,Gonococcal meningitis,Gonococcal meningitis,Other gonococcal infections,9
A560,1,A5601,Chlamydial cystitis and urethritis,Chlamydial cystitis and urethritis,Chlamydial infection of lower genitourinary tract,9
A561,1,A5611,Chlamydial female pelvic inflammatory disease,Chlamydial female pelvic inflammatory disease,Chlamydial infection of pelviperitoneum and other genitourinary organs,9
A590,1,A5901,Trichomonal vulvovaginitis,Trichomonal vulvovaginitis,Urogenital trichomoniasis,9
A600,1,A6001,Herpesviral infection of penis,Herpesviral infection of penis,Herpesviral infection of genitalia and urogenital tract,9
A66,1,A661,Multiple papillomata and wet crab yaws,Multiple papillomata and wet crab yaws,Yaws,9
A67,1,A671,Intermediate lesions of pinta,Intermediate lesions of pinta,Pinta [carate],9
A68,1,A681,Tick-borne relapsing fever,Tick-borne relapsing fever,Relapsing fevers,9
A69,1,A691,Other Vincent's infections,Other Vincent's infections,Other spirochetal infections,9
A692,1,A6921,Meningitis due to Lyme disease,Meningitis due to Lyme disease,Lyme disease,9
A71,1,A711,Active stage of trachoma,Active stage of trachoma,Trachoma,9
A748,1,A7481,Chlamydial peritonitis,Chlamydial peritonitis,Other chlamydial diseases,9
A75,1,A751,Recrudescent typhus [Brill's disease],Recrudescent typhus [Brill's disease],Typhus fever,9
A77,1,A771,Spotted fever due to Rickettsia conorii,Spotted fever due to Rickettsia conorii,Spotted fever [tick-borne rickettsioses],9
A774,1,A7741,Ehrlichiosis chafeensis [E. chafeensis],Ehrlichiosis chafeensis [E. chafeensis],Ehrlichiosis,9
A79,1,A791,Rickettsialpox due to Rickettsia akari,Rickettsialpox due to Rickettsia akari,Other rickettsioses,9
A798,1,A7981,Rickettsiosis due to Ehrlichia sennetsu,Rickettsiosis due to Ehrlichia sennetsu,Other specified rickettsioses,9
A80,1,A801,"Acute paralytic poliomyelitis, wild virus, imported","Acute paralytic poliomyelitis, wild virus, imported",Acute poliomyelitis,9
A810,1,A8101,Variant Creutzfeldt-Jakob disease,Variant Creutzfeldt-Jakob disease,Creutzfeldt-Jakob disease,9
A818,1,A8181,Kuru,Kuru,Other atypical virus infections of central nervous system,9
A82,1,A821,Urban rabies,Urban rabies,Rabies,9
A83,1,A831,Western equine encephalitis,Western equine encephalitis,Mosquito-borne viral encephalitis,9
A84,1,A841,Central European tick-borne encephalitis,Central European tick-borne encephalitis,Tick-borne viral encephalitis,9
A85,1,A851,Adenoviral encephalitis,Adenoviral encephalitis,"Other viral encephalitis, not elsewhere classified",9
A87,1,A871,Adenoviral meningitis,Adenoviral meningitis,Viral meningitis,9
A88,1,A881,Epidemic vertigo,Epidemic vertigo,"Other viral infections of central nervous system, not elsewhere classified",9
A92,1,A921,O'nyong-nyong fever,O'nyong-nyong fever,Other mosquito-borne viral fevers,9
A923,1,A9231,West Nile virus infection with encephalitis,West Nile virus infection with encephalitis,West Nile virus infection,9
A93,1,A931,Sandfly fever,Sandfly fever,"Other arthropod-borne viral fevers, not elsewhere classified",9
A95,1,A951,Urban yellow fever,Urban yellow fever,Yellow fever,9
A96,1,A961,Machupo hemorrhagic fever,Machupo hemorrhagic fever,Arenaviral hemorrhagic fever,9
A98,1,A981,Omsk hemorrhagic fever,Omsk hemorrhagic fever,"Other viral hemorrhagic fevers, not elsewhere classified",9
B00,1,B001,Herpesviral vesicular dermatitis,Herpesviral vesicular dermatitis,Herpesviral [herpes simplex] infections,9
B005,1,B0051,Herpesviral iridocyclitis,Herpesviral iridocyclitis,Herpesviral ocular disease,9
B008,1,B0081,Herpesviral hepatitis,Herpesviral hepatitis,Other forms of herpesviral infections,9
B011,1,B0111,Varicella encephalitis and encephalomyelitis,Varicella encephalitis and encephalomyelitis,"Varicella encephalitis, myelitis and encephalomyelitis",9
B018,1,B0181,Varicella keratitis,Varicella keratitis,Varicella with other complications,9
B02,1,B021,Zoster meningitis,Zoster meningitis,Zoster [herpes zoster],9
B022,1,B0221,Postherpetic geniculate ganglionitis,Postherpetic geniculate ganglionitis,Zoster with other nervous system involvement,9
B023,1,B0231,Zoster conjunctivitis,Zoster conjunctivitis,Zoster ocular disease,9
A35,0,A35,Other tetanus,Other tetanus,Other tetanus,9
B058,1,B0581,Measles keratitis and keratoconjunctivitis,Measles keratitis and keratoconjunctivitis,Measles with other complications,9
B060,1,B0601,Rubella encephalitis,Rubella encephalitis,Rubella with neurological complications,9
B068,1,B0681,Rubella pneumonia,Rubella pneumonia,Rubella with other complications,9
B0801,1,B08011,Vaccinia not from vaccine,Vaccinia not from vaccine,Cowpox and vaccinia not from vaccine,9
B082,1,B0821,Exanthema subitum [sixth disease] due to human herpesvirus 6,Exanthema subitum [sixth disease] due to human herpesvirus 6,Exanthema subitum [sixth disease],9
B086,1,B0861,Bovine stomatitis,Bovine stomatitis,Parapoxvirus infections,9
B087,1,B0871,Tanapox virus disease,Tanapox virus disease,Yatapoxvirus infections,9
B100,1,B1001,Human herpesvirus 6 encephalitis,Human herpesvirus 6 encephalitis,Other human herpesvirus encephalitis,9
B108,1,B1081,Human herpesvirus 6 infection,Human herpesvirus 6 infection,Other human herpesvirus infection,9
B16,1,B161,Acute hepatitis B with delta-agent without hepatic coma,Acute hepatitis B with delta-agent without hepatic coma,Acute hepatitis B,9
B171,1,B1711,Acute hepatitis C with hepatic coma,Acute hepatitis C with hepatic coma,Acute hepatitis C,9
B18,1,B181,Chronic viral hepatitis B without delta-agent,Chronic viral hepatitis B without delta-agent,Chronic viral hepatitis,9
B191,1,B1911,Unspecified viral hepatitis B with hepatic coma,Unspecified viral hepatitis B with hepatic coma,Unspecified viral hepatitis B,9
B192,1,B1921,Unspecified viral hepatitis C with hepatic coma,Unspecified viral hepatitis C with hepatic coma,Unspecified viral hepatitis C,9
B25,1,B251,Cytomegaloviral hepatitis,Cytomegaloviral hepatitis,Cytomegaloviral disease,9
B26,1,B261,Mumps meningitis,Mumps meningitis,Mumps,9
B268,1,B2681,Mumps hepatitis,Mumps hepatitis,Mumps with other complications,9
B270,1,B2701,Gammaherpesviral mononucleosis with polyneuropathy,Gammaherpesviral mononucleosis with polyneuropathy,Gammaherpesviral mononucleosis,9
B271,1,B2711,Cytomegaloviral mononucleosis with polyneuropathy,Cytomegaloviral mononucleosis with polyneuropathy,Cytomegaloviral mononucleosis,9
B278,1,B2781,Other infectious mononucleosis with polyneuropathy,Other infectious mononucleosis with polyneuropathy,Other infectious mononucleosis,9
B279,1,B2791,"Infectious mononucleosis, unspecified with polyneuropathy","Infectious mononucleosis, unspecified with polyneuropathy","Infectious mononucleosis, unspecified",9
B30,1,B301,Conjunctivitis due to adenovirus,Conjunctivitis due to adenovirus,Viral conjunctivitis,9
B33,1,B331,Ross River disease,Ross River disease,"Other viral diseases, not elsewhere classified",9
B332,1,B3321,Viral endocarditis,Viral endocarditis,Viral carditis,9
B34,1,B341,"Enterovirus infection, unspecified","Enterovirus infection, unspecified",Viral infection of unspecified site,9
B35,1,B351,Tinea unguium,Tinea unguium,Dermatophytosis,9
B36,1,B361,Tinea nigra,Tinea nigra,Other superficial mycoses,9
B37,1,B371,Pulmonary candidiasis,Pulmonary candidiasis,Candidiasis,9
B374,1,B3741,Candidal cystitis and urethritis,Candidal cystitis and urethritis,Candidiasis of other urogenital sites,9
B378,1,B3781,Candidal esophagitis,Candidal esophagitis,Candidiasis of other sites,9
B38,1,B381,Chronic pulmonary coccidioidomycosis,Chronic pulmonary coccidioidomycosis,Coccidioidomycosis,9
B388,1,B3881,Prostatic coccidioidomycosis,Prostatic coccidioidomycosis,Other forms of coccidioidomycosis,9
B39,1,B391,Chronic pulmonary histoplasmosis capsulati,Chronic pulmonary histoplasmosis capsulati,Histoplasmosis,9
B40,1,B401,Chronic pulmonary blastomycosis,Chronic pulmonary blastomycosis,Blastomycosis,9
B408,1,B4081,Blastomycotic meningoencephalitis,Blastomycotic meningoencephalitis,Other forms of blastomycosis,9
B42,1,B421,Lymphocutaneous sporotrichosis,Lymphocutaneous sporotrichosis,Sporotrichosis,9
B428,1,B4281,Cerebral sporotrichosis,Cerebral sporotrichosis,Other forms of sporotrichosis,9
B43,1,B431,Pheomycotic brain abscess,Pheomycotic brain abscess,Chromomycosis and pheomycotic abscess,9
B44,1,B441,Other pulmonary aspergillosis,Other pulmonary aspergillosis,Aspergillosis,9
B448,1,B4481,Allergic bronchopulmonary aspergillosis,Allergic bronchopulmonary aspergillosis,Other forms of aspergillosis,9
B45,1,B451,Cerebral cryptococcosis,Cerebral cryptococcosis,Cryptococcosis,9
B46,1,B461,Rhinocerebral mucormycosis,Rhinocerebral mucormycosis,Zygomycosis,9
B47,1,B471,Actinomycetoma,Actinomycetoma,Mycetoma,9
B48,1,B481,Rhinosporidiosis,Rhinosporidiosis,"Other mycoses, not elsewhere classified",9
B53,1,B531,Malaria due to simian plasmodia,Malaria due to simian plasmodia,Other specified malaria,9
B55,1,B551,Cutaneous leishmaniasis,Cutaneous leishmaniasis,Leishmaniasis,9
B56,1,B561,Rhodesiense trypanosomiasis,Rhodesiense trypanosomiasis,African trypanosomiasis,9
B57,1,B571,Acute Chagas' disease without heart involvement,Acute Chagas' disease without heart involvement,Chagas' disease,9
B573,1,B5731,Megaesophagus in Chagas' disease,Megaesophagus in Chagas' disease,Chagas' disease (chronic) with digestive system involvement,9
B574,1,B5741,Meningitis in Chagas' disease,Meningitis in Chagas' disease,Chagas' disease (chronic) with nervous system involvement,9
B580,1,B5801,Toxoplasma chorioretinitis,Toxoplasma chorioretinitis,Toxoplasma oculopathy,9
B588,1,B5881,Toxoplasma myocarditis,Toxoplasma myocarditis,Toxoplasmosis with other organ involvement,9
B601,1,B6011,Meningoencephalitis due to Acanthamoeba (culbertsoni),Meningoencephalitis due to Acanthamoeba (culbertsoni),Acanthamebiasis,9
B65,1,B651,Schistosomiasis due to Schistosoma mansoni,Schistosomiasis due to Schistosoma mansoni [intestinal schistosomiasis],Schistosomiasis [bilharziasis],9
B66,1,B661,Clonorchiasis,Clonorchiasis,Other fluke infections,9
B67,1,B671,Echinococcus granulosus infection of lung,Echinococcus granulosus infection of lung,Echinococcosis,9
D738,1,D7381,Neutropenic splenomegaly,Neutropenic splenomegaly,Other diseases of spleen,9
B673,1,B6731,"Echinococcus granulosus infection, thyroid gland","Echinococcus granulosus infection, thyroid gland","Echinococcus granulosus infection, other and multiple sites",9
B676,1,B6761,"Echinococcus multilocularis infection, multiple sites","Echinococcus multilocularis infection, multiple sites","Echinococcus multilocularis infection, other and multiple sites",9
B68,1,B681,Taenia saginata taeniasis,Taenia saginata taeniasis,Taeniasis,9
B69,1,B691,Cysticercosis of eye,Cysticercosis of eye,Cysticercosis,9
B698,1,B6981,Myositis in cysticercosis,Myositis in cysticercosis,Cysticercosis of other sites,9
B70,1,B701,Sparganosis,Sparganosis,Diphyllobothriasis and sparganosis,9
B71,1,B711,Dipylidiasis,Dipylidiasis,Other cestode infections,9
B730,1,B7301,Onchocerciasis with endophthalmitis,Onchocerciasis with endophthalmitis,Onchocerciasis with eye disease,9
B74,1,B741,Filariasis due to Brugia malayi,Filariasis due to Brugia malayi,Filariasis,9
B76,1,B761,Necatoriasis,Necatoriasis,Hookworm diseases,9
B778,1,B7781,Ascariasis pneumonia,Ascariasis pneumonia,Ascariasis with other complications,9
B78,1,B781,Cutaneous strongyloidiasis,Cutaneous strongyloidiasis,Strongyloidiasis,9
B81,1,B811,Intestinal capillariasis,Intestinal capillariasis,"Other intestinal helminthiases, not elsewhere classified",9
B83,1,B831,Gnathostomiasis,Gnathostomiasis,Other helminthiases,9
B85,1,B851,Pediculosis due to Pediculus humanus corporis,Pediculosis due to Pediculus humanus corporis,Pediculosis and phthiriasis,9
B87,1,B871,Wound myiasis,Wound myiasis,Myiasis,9
B878,1,B8781,Genitourinary myiasis,Genitourinary myiasis,Myiasis of other sites,9
B88,1,B881,Tungiasis [sandflea infestation],Tungiasis [sandflea infestation],Other infestations,9
B90,1,B901,Sequelae of genitourinary tuberculosis,Sequelae of genitourinary tuberculosis,Sequelae of tuberculosis,9
B94,1,B941,Sequelae of viral encephalitis,Sequelae of viral encephalitis,Sequelae of other and unspecified infectious and parasitic diseases,9
B95,1,B951,"Streptococcus, group B, causing diseases classd elswhr","Streptococcus, group B, as the cause of diseases classified elsewhere","Streptococcus, Staphylococcus, and Enterococcus as the cause of diseases classified elsewhere",9
B956,1,B9561,Methicillin suscep staph infct causing dis classd elswhr,Methicillin susceptible Staphylococcus aureus infection as the cause of diseases classified elsewhere,Staphylococcus aureus as the cause of diseases classified elsewhere,9
B96,1,B961,Klebsiella pneumoniae as the cause of diseases classd elswhr,Klebsiella pneumoniae [K. pneumoniae] as the cause of diseases classified elsewhere,Other bacterial agents as the cause of diseases classified elsewhere,9
B962,1,B9621,Shiga toxin E coli (STEC) O157 causing dis classd elswhr,Shiga toxin-producing Escherichia coli [E. coli] (STEC) O157 as the cause of diseases classified elsewhere,Escherichia coli [E. coli ] as the cause of diseases classified elsewhere,9
B968,1,B9681,Helicobacter pylori as the cause of diseases classd elswhr,Helicobacter pylori [H. pylori] as the cause of diseases classified elsewhere,Other specified bacterial agents as the cause of diseases classified elsewhere,9
B971,1,B9711,Coxsackievirus as the cause of diseases classified elsewhere,Coxsackievirus as the cause of diseases classified elsewhere,Enterovirus as the cause of diseases classified elsewhere,9
B972,1,B9721,SARS-associated coronavirus causing diseases classd elswhr,SARS-associated coronavirus as the cause of diseases classified elsewhere,Coronavirus as the cause of diseases classified elsewhere,9
B973,1,B9731,Lentivirus as the cause of diseases classified elsewhere,Lentivirus as the cause of diseases classified elsewhere,Retrovirus as the cause of diseases classified elsewhere,9
B978,1,B9781,Human metapneumovirus as the cause of diseases classd elswhr,Human metapneumovirus as the cause of diseases classified elsewhere,Other viral agents as the cause of diseases classified elsewhere,9
C00,1,C001,Malignant neoplasm of external lower lip,Malignant neoplasm of external lower lip,Malignant neoplasm of lip,9
C02,1,C021,Malignant neoplasm of border of tongue,Malignant neoplasm of border of tongue,Malignant neoplasm of other and unspecified parts of tongue,9
C03,1,C031,Malignant neoplasm of lower gum,Malignant neoplasm of lower gum,Malignant neoplasm of gum,9
C04,1,C041,Malignant neoplasm of lateral floor of mouth,Malignant neoplasm of lateral floor of mouth,Malignant neoplasm of floor of mouth,9
C05,1,C051,Malignant neoplasm of soft palate,Malignant neoplasm of soft palate,Malignant neoplasm of palate,9
C06,1,C061,Malignant neoplasm of vestibule of mouth,Malignant neoplasm of vestibule of mouth,Malignant neoplasm of other and unspecified parts of mouth,9
C08,1,C081,Malignant neoplasm of sublingual gland,Malignant neoplasm of sublingual gland,Malignant neoplasm of other and unspecified major salivary glands,9
C09,1,C091,Malig neoplasm of tonsillar pillar (anterior) (posterior),Malignant neoplasm of tonsillar pillar (anterior) (posterior),Malignant neoplasm of tonsil,9
C10,1,C101,Malignant neoplasm of anterior surface of epiglottis,Malignant neoplasm of anterior surface of epiglottis,Malignant neoplasm of oropharynx,9
C11,1,C111,Malignant neoplasm of posterior wall of nasopharynx,Malignant neoplasm of posterior wall of nasopharynx,Malignant neoplasm of nasopharynx,9
C13,1,C131,"Malig neoplasm of aryepiglottic fold, hypopharyngeal aspect","Malignant neoplasm of aryepiglottic fold, hypopharyngeal aspect",Malignant neoplasm of hypopharynx,9
C16,1,C161,Malignant neoplasm of fundus of stomach,Malignant neoplasm of fundus of stomach,Malignant neoplasm of stomach,9
C17,1,C171,Malignant neoplasm of jejunum,Malignant neoplasm of jejunum,Malignant neoplasm of small intestine,9
C18,1,C181,Malignant neoplasm of appendix,Malignant neoplasm of appendix,Malignant neoplasm of colon,9
C21,1,C211,Malignant neoplasm of anal canal,Malignant neoplasm of anal canal,Malignant neoplasm of anus and anal canal,9
C22,1,C221,Intrahepatic bile duct carcinoma,Intrahepatic bile duct carcinoma,Malignant neoplasm of liver and intrahepatic bile ducts,9
C24,1,C241,Malignant neoplasm of ampulla of Vater,Malignant neoplasm of ampulla of Vater,Malignant neoplasm of other and unspecified parts of biliary tract,9
C25,1,C251,Malignant neoplasm of body of pancreas,Malignant neoplasm of body of pancreas,Malignant neoplasm of pancreas,9
C26,1,C261,Malignant neoplasm of spleen,Malignant neoplasm of spleen,Malignant neoplasm of other and ill-defined digestive organs,9
C30,1,C301,Malignant neoplasm of middle ear,Malignant neoplasm of middle ear,Malignant neoplasm of nasal cavity and middle ear,9
C31,1,C311,Malignant neoplasm of ethmoidal sinus,Malignant neoplasm of ethmoidal sinus,Malignant neoplasm of accessory sinuses,9
C32,1,C321,Malignant neoplasm of supraglottis,Malignant neoplasm of supraglottis,Malignant neoplasm of larynx,9
C340,1,C3401,Malignant neoplasm of right main bronchus,Malignant neoplasm of right main bronchus,Malignant neoplasm of main bronchus,9
C341,1,C3411,"Malignant neoplasm of upper lobe, right bronchus or lung","Malignant neoplasm of upper lobe, right bronchus or lung","Malignant neoplasm of upper lobe, bronchus or lung",9
C343,1,C3431,"Malignant neoplasm of lower lobe, right bronchus or lung","Malignant neoplasm of lower lobe, right bronchus or lung","Malignant neoplasm of lower lobe, bronchus or lung",9
C348,1,C3481,Malignant neoplasm of ovrlp sites of right bronchus and lung,Malignant neoplasm of overlapping sites of right bronchus and lung,Malignant neoplasm of overlapping sites of bronchus and lung,9
C349,1,C3491,Malignant neoplasm of unsp part of right bronchus or lung,Malignant neoplasm of unspecified part of right bronchus or lung,Malignant neoplasm of unspecified part of bronchus or lung,9
C38,1,C381,Malignant neoplasm of anterior mediastinum,Malignant neoplasm of anterior mediastinum,"Malignant neoplasm of heart, mediastinum and pleura",9
C400,1,C4001,Malig neoplasm of scapula and long bones of right upper limb,Malignant neoplasm of scapula and long bones of right upper limb,Malignant neoplasm of scapula and long bones of upper limb,9
C401,1,C4011,Malignant neoplasm of short bones of right upper limb,Malignant neoplasm of short bones of right upper limb,Malignant neoplasm of short bones of upper limb,9
C402,1,C4021,Malignant neoplasm of long bones of right lower limb,Malignant neoplasm of long bones of right lower limb,Malignant neoplasm of long bones of lower limb,9
C403,1,C4031,Malignant neoplasm of short bones of right lower limb,Malignant neoplasm of short bones of right lower limb,Malignant neoplasm of short bones of lower limb,9
C408,1,C4081,Malig neoplm of ovrlp sites of bone/artic cartl of r limb,Malignant neoplasm of overlapping sites of bone and articular cartilage of right limb,Malignant neoplasm of overlapping sites of bone and articular cartilage of limb,9
C409,1,C4091,Malig neoplasm of unsp bones and artic cartlg of right limb,Malignant neoplasm of unspecified bones and articular cartilage of right limb,Malignant neoplasm of unspecified bones and articular cartilage of limb,9
C41,1,C411,Malignant neoplasm of mandible,Malignant neoplasm of mandible,Malignant neoplasm of bone and articular cartilage of other and unspecified sites,9
C431,1,C4311,"Malignant melanoma of right eyelid, including canthus","Malignant melanoma of right eyelid, including canthus","Malignant melanoma of eyelid, including canthus",9
C432,1,C4321,Malignant melanoma of right ear and external auricular canal,Malignant melanoma of right ear and external auricular canal,Malignant melanoma of ear and external auricular canal,9
C433,1,C4331,Malignant melanoma of nose,Malignant melanoma of nose,Malignant melanoma of other and unspecified parts of face,9
C435,1,C4351,Malignant melanoma of anal skin,Malignant melanoma of anal skin,Malignant melanoma of trunk,9
C436,1,C4361,"Malignant melanoma of right upper limb, including shoulder","Malignant melanoma of right upper limb, including shoulder","Malignant melanoma of upper limb, including shoulder",9
C437,1,C4371,"Malignant melanoma of right lower limb, including hip","Malignant melanoma of right lower limb, including hip","Malignant melanoma of lower limb, including hip",9
C4A1,1,C4A11,"Merkel cell carcinoma of right eyelid, including canthus","Merkel cell carcinoma of right eyelid, including canthus","Merkel cell carcinoma of eyelid, including canthus",9
C4A2,1,C4A21,Merkel cell carcinoma of right ear and external auric canal,Merkel cell carcinoma of right ear and external auricular canal,Merkel cell carcinoma of ear and external auricular canal,9
C4A3,1,C4A31,Merkel cell carcinoma of nose,Merkel cell carcinoma of nose,Merkel cell carcinoma of other and unspecified parts of face,9
C4A5,1,C4A51,Merkel cell carcinoma of anal skin,Merkel cell carcinoma of anal skin,Merkel cell carcinoma of trunk,9
C4A6,1,C4A61,"Merkel cell carcinoma of right upper limb, inc shoulder","Merkel cell carcinoma of right upper limb, including shoulder","Merkel cell carcinoma of upper limb, including shoulder",9
C4A7,1,C4A71,"Merkel cell carcinoma of right lower limb, including hip","Merkel cell carcinoma of right lower limb, including hip","Merkel cell carcinoma of lower limb, including hip",9
C440,1,C4401,Basal cell carcinoma of skin of lip,Basal cell carcinoma of skin of lip,Other and unspecified malignant neoplasm of skin of lip,9
C4410,1,C44101,"Unsp malignant neoplasm skin/ unsp eyelid, including canthus","Unspecified malignant neoplasm of skin of unspecified eyelid, including canthus","Unspecified malignant neoplasm of skin of eyelid, including canthus",9
C4411,1,C44111,"Basal cell carcinoma skin/ unsp eyelid, including canthus","Basal cell carcinoma of skin of unspecified eyelid, including canthus","Basal cell carcinoma of skin of eyelid, including canthus",9
C4412,1,C44121,"Squamous cell carcinoma skin/ unsp eyelid, including canthus","Squamous cell carcinoma of skin of unspecified eyelid, including canthus","Squamous cell carcinoma of skin of eyelid, including canthus",9
C4419,1,C44191,"Oth malignant neoplasm skin/ unsp eyelid, including canthus","Other specified malignant neoplasm of skin of unspecified eyelid, including canthus","Other specified malignant neoplasm of skin of eyelid, including canthus",9
C4420,1,C44201,Unsp malig neoplasm skin/ unsp ear and external auric canal,Unspecified malignant neoplasm of skin of unspecified ear and external auricular canal,Unspecified malignant neoplasm of skin of ear and external auricular canal,9
C4421,1,C44211,Basal cell carcinoma skin/ unsp ear and external auric canal,Basal cell carcinoma of skin of unspecified ear and external auricular canal,Basal cell carcinoma of skin of ear and external auricular canal,9
C4422,1,C44221,Squamous cell carcinoma skin/ unsp ear and extrn auric canal,Squamous cell carcinoma of skin of unspecified ear and external auricular canal,Squamous cell carcinoma of skin of ear and external auricular canal,9
C724,1,C7241,Malignant neoplasm of right acoustic nerve,Malignant neoplasm of right acoustic nerve,Malignant neoplasm of acoustic nerve,9
C4429,1,C44291,Oth malig neoplasm skin/ unsp ear and external auric canal,Other specified malignant neoplasm of skin of unspecified ear and external auricular canal,Other specified malignant neoplasm of skin of ear and external auricular canal,9
C4430,1,C44301,Unspecified malignant neoplasm of skin of nose,Unspecified malignant neoplasm of skin of nose,Unspecified malignant neoplasm of skin of other and unspecified parts of face,9
C4431,1,C44311,Basal cell carcinoma of skin of nose,Basal cell carcinoma of skin of nose,Basal cell carcinoma of skin of other and unspecified parts of face,9
C4432,1,C44321,Squamous cell carcinoma of skin of nose,Squamous cell carcinoma of skin of nose,Squamous cell carcinoma of skin of other and unspecified parts of face,9
C4439,1,C44391,Other specified malignant neoplasm of skin of nose,Other specified malignant neoplasm of skin of nose,Other specified malignant neoplasm of skin of other and unspecified parts of face,9
C444,1,C4441,Basal cell carcinoma of skin of scalp and neck,Basal cell carcinoma of skin of scalp and neck,Other and unspecified malignant neoplasm of skin of scalp and neck,9
C4450,1,C44501,Unspecified malignant neoplasm of skin of breast,Unspecified malignant neoplasm of skin of breast,Unspecified malignant neoplasm of skin of trunk,9
C4451,1,C44511,Basal cell carcinoma of skin of breast,Basal cell carcinoma of skin of breast,Basal cell carcinoma of skin of trunk,9
C4452,1,C44521,Squamous cell carcinoma of skin of breast,Squamous cell carcinoma of skin of breast,Squamous cell carcinoma of skin of trunk,9
C4459,1,C44591,Other specified malignant neoplasm of skin of breast,Other specified malignant neoplasm of skin of breast,Other specified malignant neoplasm of skin of trunk,9
C4460,1,C44601,"Unsp malignant neoplasm skin/ unsp upper limb, inc shoulder","Unspecified malignant neoplasm of skin of unspecified upper limb, including shoulder","Unspecified malignant neoplasm of skin of upper limb, including shoulder",9
C4461,1,C44611,"Basal cell carcinoma skin/ unsp upper limb, inc shoulder","Basal cell carcinoma of skin of unspecified upper limb, including shoulder","Basal cell carcinoma of skin of upper limb, including shoulder",9
C4462,1,C44621,"Squamous cell carcinoma skin/ unsp upper limb, inc shoulder","Squamous cell carcinoma of skin of unspecified upper limb, including shoulder","Squamous cell carcinoma of skin of upper limb, including shoulder",9
C4469,1,C44691,"Oth malignant neoplasm skin/ unsp upper limb, inc shoulder","Other specified malignant neoplasm of skin of unspecified upper limb, including shoulder","Other specified malignant neoplasm of skin of upper limb, including shoulder",9
C4470,1,C44701,"Unsp malignant neoplasm skin/ unsp lower limb, including hip","Unspecified malignant neoplasm of skin of unspecified lower limb, including hip","Unspecified malignant neoplasm of skin of lower limb, including hip",9
C4471,1,C44711,"Basal cell carcinoma skin/ unsp lower limb, including hip","Basal cell carcinoma of skin of unspecified lower limb, including hip","Basal cell carcinoma of skin of lower limb, including hip",9
C4472,1,C44721,"Squamous cell carcinoma skin/ unsp lower limb, including hip","Squamous cell carcinoma of skin of unspecified lower limb, including hip","Squamous cell carcinoma of skin of lower limb, including hip",9
C4479,1,C44791,"Oth malignant neoplasm skin/ unsp lower limb, including hip","Other specified malignant neoplasm of skin of unspecified lower limb, including hip","Other specified malignant neoplasm of skin of lower limb, including hip",9
C448,1,C4481,Basal cell carcinoma of overlapping sites of skin,Basal cell carcinoma of overlapping sites of skin,Other and unspecified malignant neoplasm of overlapping sites of skin,9
C449,1,C4491,"Basal cell carcinoma of skin, unspecified","Basal cell carcinoma of skin, unspecified","Other and unspecified malignant neoplasm of skin, unspecified",9
C45,1,C451,Mesothelioma of peritoneum,Mesothelioma of peritoneum,Mesothelioma,9
C46,1,C461,Kaposi's sarcoma of soft tissue,Kaposi's sarcoma of soft tissue,Kaposi's sarcoma,9
C465,1,C4651,Kaposi's sarcoma of right lung,Kaposi's sarcoma of right lung,Kaposi's sarcoma of lung,9
C471,1,C4711,"Malig neoplm of prph nerves of right upper limb, inc shldr","Malignant neoplasm of peripheral nerves of right upper limb, including shoulder","Malignant neoplasm of peripheral nerves of upper limb, including shoulder",9
C472,1,C4721,"Malig neoplasm of prph nerves of right lower limb, inc hip","Malignant neoplasm of peripheral nerves of right lower limb, including hip","Malignant neoplasm of peripheral nerves of lower limb, including hip",9
C48,1,C481,Malignant neoplasm of specified parts of peritoneum,Malignant neoplasm of specified parts of peritoneum,Malignant neoplasm of retroperitoneum and peritoneum,9
C491,1,C4911,"Malig neoplm of conn and soft tiss of r upr limb, inc shldr","Malignant neoplasm of connective and soft tissue of right upper limb, including shoulder","Malignant neoplasm of connective and soft tissue of upper limb, including shoulder",9
C492,1,C4921,"Malig neoplm of conn and soft tiss of r low limb, inc hip","Malignant neoplasm of connective and soft tissue of right lower limb, including hip","Malignant neoplasm of connective and soft tissue of lower limb, including hip",9
C49A,1,C49A1,Gastrointestinal stromal tumor of esophagus,Gastrointestinal stromal tumor of esophagus,Gastrointestinal stromal tumor,9
C5001,1,C50011,"Malignant neoplasm of nipple and areola, right female breast","Malignant neoplasm of nipple and areola, right female breast","Malignant neoplasm of nipple and areola, female",9
C5002,1,C50021,"Malignant neoplasm of nipple and areola, right male breast","Malignant neoplasm of nipple and areola, right male breast","Malignant neoplasm of nipple and areola, male",9
C5011,1,C50111,Malignant neoplasm of central portion of right female breast,Malignant neoplasm of central portion of right female breast,"Malignant neoplasm of central portion of breast, female",9
C5012,1,C50121,Malignant neoplasm of central portion of right male breast,Malignant neoplasm of central portion of right male breast,"Malignant neoplasm of central portion of breast, male",9
C5021,1,C50211,Malig neoplm of upper-inner quadrant of right female breast,Malignant neoplasm of upper-inner quadrant of right female breast,"Malignant neoplasm of upper-inner quadrant of breast, female",9
C5022,1,C50221,Malig neoplasm of upper-inner quadrant of right male breast,Malignant neoplasm of upper-inner quadrant of right male breast,"Malignant neoplasm of upper-inner quadrant of breast, male",9
C5031,1,C50311,Malig neoplm of lower-inner quadrant of right female breast,Malignant neoplasm of lower-inner quadrant of right female breast,"Malignant neoplasm of lower-inner quadrant of breast, female",9
C5032,1,C50321,Malig neoplasm of lower-inner quadrant of right male breast,Malignant neoplasm of lower-inner quadrant of right male breast,"Malignant neoplasm of lower-inner quadrant of breast, male",9
C5041,1,C50411,Malig neoplm of upper-outer quadrant of right female breast,Malignant neoplasm of upper-outer quadrant of right female breast,"Malignant neoplasm of upper-outer quadrant of breast, female",9
C5042,1,C50421,Malig neoplasm of upper-outer quadrant of right male breast,Malignant neoplasm of upper-outer quadrant of right male breast,"Malignant neoplasm of upper-outer quadrant of breast, male",9
C5051,1,C50511,Malig neoplm of lower-outer quadrant of right female breast,Malignant neoplasm of lower-outer quadrant of right female breast,"Malignant neoplasm of lower-outer quadrant of breast, female",9
C5052,1,C50521,Malig neoplasm of lower-outer quadrant of right male breast,Malignant neoplasm of lower-outer quadrant of right male breast,"Malignant neoplasm of lower-outer quadrant of breast, male",9
C5061,1,C50611,Malignant neoplasm of axillary tail of right female breast,Malignant neoplasm of axillary tail of right female breast,"Malignant neoplasm of axillary tail of breast, female",9
C5062,1,C50621,Malignant neoplasm of axillary tail of right male breast,Malignant neoplasm of axillary tail of right male breast,"Malignant neoplasm of axillary tail of breast, male",9
C5081,1,C50811,Malignant neoplasm of ovrlp sites of right female breast,Malignant neoplasm of overlapping sites of right female breast,"Malignant neoplasm of overlapping sites of breast, female",9
C5082,1,C50821,Malignant neoplasm of overlapping sites of right male breast,Malignant neoplasm of overlapping sites of right male breast,"Malignant neoplasm of overlapping sites of breast, male",9
C5091,1,C50911,Malignant neoplasm of unsp site of right female breast,Malignant neoplasm of unspecified site of right female breast,"Malignant neoplasm of breast of unspecified site, female",9
C5092,1,C50921,Malignant neoplasm of unspecified site of right male breast,Malignant neoplasm of unspecified site of right male breast,"Malignant neoplasm of breast of unspecified site, male",9
C51,1,C511,Malignant neoplasm of labium minus,Malignant neoplasm of labium minus,Malignant neoplasm of vulva,9
C53,1,C531,Malignant neoplasm of exocervix,Malignant neoplasm of exocervix,Malignant neoplasm of cervix uteri,9
C54,1,C541,Malignant neoplasm of endometrium,Malignant neoplasm of endometrium,Malignant neoplasm of corpus uteri,9
C56,1,C561,Malignant neoplasm of right ovary,Malignant neoplasm of right ovary,Malignant neoplasm of ovary,9
C570,1,C5701,Malignant neoplasm of right fallopian tube,Malignant neoplasm of right fallopian tube,Malignant neoplasm of fallopian tube,9
C571,1,C5711,Malignant neoplasm of right broad ligament,Malignant neoplasm of right broad ligament,Malignant neoplasm of broad ligament,9
C572,1,C5721,Malignant neoplasm of right round ligament,Malignant neoplasm of right round ligament,Malignant neoplasm of round ligament,9
C60,1,C601,Malignant neoplasm of glans penis,Malignant neoplasm of glans penis,Malignant neoplasm of penis,9
C620,1,C6201,Malignant neoplasm of undescended right testis,Malignant neoplasm of undescended right testis,Malignant neoplasm of undescended testis,9
C621,1,C6211,Malignant neoplasm of descended right testis,Malignant neoplasm of descended right testis,Malignant neoplasm of descended testis,9
C629,1,C6291,"Malig neoplm of right testis, unsp descended or undescended","Malignant neoplasm of right testis, unspecified whether descended or undescended","Malignant neoplasm of testis, unspecified whether descended or undescended",9
C630,1,C6301,Malignant neoplasm of right epididymis,Malignant neoplasm of right epididymis,Malignant neoplasm of epididymis,9
C631,1,C6311,Malignant neoplasm of right spermatic cord,Malignant neoplasm of right spermatic cord,Malignant neoplasm of spermatic cord,9
C64,1,C641,"Malignant neoplasm of right kidney, except renal pelvis","Malignant neoplasm of right kidney, except renal pelvis","Malignant neoplasm of kidney, except renal pelvis",9
C65,1,C651,Malignant neoplasm of right renal pelvis,Malignant neoplasm of right renal pelvis,Malignant neoplasm of renal pelvis,9
C66,1,C661,Malignant neoplasm of right ureter,Malignant neoplasm of right ureter,Malignant neoplasm of ureter,9
C67,1,C671,Malignant neoplasm of dome of bladder,Malignant neoplasm of dome of bladder,Malignant neoplasm of bladder,9
C68,1,C681,Malignant neoplasm of paraurethral glands,Malignant neoplasm of paraurethral glands,Malignant neoplasm of other and unspecified urinary organs,9
C690,1,C6901,Malignant neoplasm of right conjunctiva,Malignant neoplasm of right conjunctiva,Malignant neoplasm of conjunctiva,9
C691,1,C6911,Malignant neoplasm of right cornea,Malignant neoplasm of right cornea,Malignant neoplasm of cornea,9
C692,1,C6921,Malignant neoplasm of right retina,Malignant neoplasm of right retina,Malignant neoplasm of retina,9
C693,1,C6931,Malignant neoplasm of right choroid,Malignant neoplasm of right choroid,Malignant neoplasm of choroid,9
C694,1,C6941,Malignant neoplasm of right ciliary body,Malignant neoplasm of right ciliary body,Malignant neoplasm of ciliary body,9
C695,1,C6951,Malignant neoplasm of right lacrimal gland and duct,Malignant neoplasm of right lacrimal gland and duct,Malignant neoplasm of lacrimal gland and duct,9
C696,1,C6961,Malignant neoplasm of right orbit,Malignant neoplasm of right orbit,Malignant neoplasm of orbit,9
C698,1,C6981,Malignant neoplasm of ovrlp sites of right eye and adnexa,Malignant neoplasm of overlapping sites of right eye and adnexa,Malignant neoplasm of overlapping sites of eye and adnexa,9
C699,1,C6991,Malignant neoplasm of unspecified site of right eye,Malignant neoplasm of unspecified site of right eye,Malignant neoplasm of unspecified site of eye,9
C70,1,C701,Malignant neoplasm of spinal meninges,Malignant neoplasm of spinal meninges,Malignant neoplasm of meninges,9
C71,1,C711,Malignant neoplasm of frontal lobe,Malignant neoplasm of frontal lobe,Malignant neoplasm of brain,9
C72,1,C721,Malignant neoplasm of cauda equina,Malignant neoplasm of cauda equina,"Malignant neoplasm of spinal cord, cranial nerves and other parts of central nervous system",9
C722,1,C7221,Malignant neoplasm of right olfactory nerve,Malignant neoplasm of right olfactory nerve,Malignant neoplasm of olfactory nerve,9
C723,1,C7231,Malignant neoplasm of right optic nerve,Malignant neoplasm of right optic nerve,Malignant neoplasm of optic nerve,9
C740,1,C7401,Malignant neoplasm of cortex of right adrenal gland,Malignant neoplasm of cortex of right adrenal gland,Malignant neoplasm of cortex of adrenal gland,9
C741,1,C7411,Malignant neoplasm of medulla of right adrenal gland,Malignant neoplasm of medulla of right adrenal gland,Malignant neoplasm of medulla of adrenal gland,9
C749,1,C7491,Malignant neoplasm of unsp part of right adrenal gland,Malignant neoplasm of unspecified part of right adrenal gland,Malignant neoplasm of unspecified part of adrenal gland,9
C75,1,C751,Malignant neoplasm of pituitary gland,Malignant neoplasm of pituitary gland,Malignant neoplasm of other endocrine glands and related structures,9
C7A01,1,C7A011,Malignant carcinoid tumor of the jejunum,Malignant carcinoid tumor of the jejunum,Malignant carcinoid tumors of the small intestine,9
C7A02,1,C7A021,Malignant carcinoid tumor of the cecum,Malignant carcinoid tumor of the cecum,"Malignant carcinoid tumors of the appendix, large intestine, and rectum",9
C7A09,1,C7A091,Malignant carcinoid tumor of the thymus,Malignant carcinoid tumor of the thymus,Malignant carcinoid tumors of other sites,9
C7B0,1,C7B01,Secondary carcinoid tumors of distant lymph nodes,Secondary carcinoid tumors of distant lymph nodes,Secondary carcinoid tumors,9
C76,1,C761,Malignant neoplasm of thorax,Malignant neoplasm of thorax,Malignant neoplasm of other and ill-defined sites,9
C764,1,C7641,Malignant neoplasm of right upper limb,Malignant neoplasm of right upper limb,Malignant neoplasm of upper limb,9
C765,1,C7651,Malignant neoplasm of right lower limb,Malignant neoplasm of right lower limb,Malignant neoplasm of lower limb,9
C77,1,C771,Secondary and unsp malignant neoplasm of intrathorac nodes,Secondary and unspecified malignant neoplasm of intrathoracic lymph nodes,Secondary and unspecified malignant neoplasm of lymph nodes,9
C780,1,C7801,Secondary malignant neoplasm of right lung,Secondary malignant neoplasm of right lung,Secondary malignant neoplasm of lung,9
C790,1,C7901,Secondary malignant neoplasm of r kidney and renal pelvis,Secondary malignant neoplasm of right kidney and renal pelvis,Secondary malignant neoplasm of kidney and renal pelvis,9
C791,1,C7911,Secondary malignant neoplasm of bladder,Secondary malignant neoplasm of bladder,Secondary malignant neoplasm of bladder and other and unspecified urinary organs,9
C793,1,C7931,Secondary malignant neoplasm of brain,Secondary malignant neoplasm of brain,Secondary malignant neoplasm of brain and cerebral meninges,9
C795,1,C7951,Secondary malignant neoplasm of bone,Secondary malignant neoplasm of bone,Secondary malignant neoplasm of bone and bone marrow,9
C796,1,C7961,Secondary malignant neoplasm of right ovary,Secondary malignant neoplasm of right ovary,Secondary malignant neoplasm of ovary,9
C797,1,C7971,Secondary malignant neoplasm of right adrenal gland,Secondary malignant neoplasm of right adrenal gland,Secondary malignant neoplasm of adrenal gland,9
C798,1,C7981,Secondary malignant neoplasm of breast,Secondary malignant neoplasm of breast,Secondary malignant neoplasm of other specified sites,9
C80,1,C801,"Malignant (primary) neoplasm, unspecified","Malignant (primary) neoplasm, unspecified",Malignant neoplasm without specification of site,9
C810,1,C8101,"Nodlr lymphocy predom Hdgkn lymph, nodes of head, face, & nk","Nodular lymphocyte predominant Hodgkin lymphoma, lymph nodes of head, face, and neck",Nodular lymphocyte predominant Hodgkin lymphoma,9
C811,1,C8111,"Nodular scler Hodgkin lymph, nodes of head, face, and neck","Nodular sclerosis Hodgkin lymphoma, lymph nodes of head, face, and neck",Nodular sclerosis Hodgkin lymphoma,9
C812,1,C8121,"Mixed cellular Hodgkin lymph, nodes of head, face, and neck","Mixed cellularity Hodgkin lymphoma, lymph nodes of head, face, and neck",Mixed cellularity Hodgkin lymphoma,9
C813,1,C8131,"Lymphocy deplet Hodgkin lymph, nodes of head, face, and neck","Lymphocyte depleted Hodgkin lymphoma, lymph nodes of head, face, and neck",Lymphocyte depleted Hodgkin lymphoma,9
C814,1,C8141,"Lymp-rich Hodgkin lymphoma, nodes of head, face, and neck","Lymphocyte-rich Hodgkin lymphoma, lymph nodes of head, face, and neck",Lymphocyte-rich Hodgkin lymphoma,9
C817,1,C8171,"Other Hodgkin lymphoma, lymph nodes of head, face, and neck","Other Hodgkin lymphoma, lymph nodes of head, face, and neck",Other Hodgkin lymphoma,9
C819,1,C8191,"Hodgkin lymphoma, unsp, lymph nodes of head, face, and neck","Hodgkin lymphoma, unspecified, lymph nodes of head, face, and neck","Hodgkin lymphoma, unspecified",9
C820,1,C8201,"Follicular lymphoma grade I, nodes of head, face, and neck","Follicular lymphoma grade I, lymph nodes of head, face, and neck",Follicular lymphoma grade I,9
C821,1,C8211,"Follicular lymphoma grade II, nodes of head, face, and neck","Follicular lymphoma grade II, lymph nodes of head, face, and neck",Follicular lymphoma grade II,9
C822,1,C8221,"Foliclar lymph grade III, unsp, nodes of head, face, and nk","Follicular lymphoma grade III, unspecified, lymph nodes of head, face, and neck","Follicular lymphoma grade III, unspecified",9
C823,1,C8231,"Foliclar lymphoma grade IIIa, nodes of head, face, and neck","Follicular lymphoma grade IIIa, lymph nodes of head, face, and neck",Follicular lymphoma grade IIIa,9
C824,1,C8241,"Foliclar lymphoma grade IIIb, nodes of head, face, and neck","Follicular lymphoma grade IIIb, lymph nodes of head, face, and neck",Follicular lymphoma grade IIIb,9
C825,1,C8251,"Diffuse folicl center lymph, nodes of head, face, and neck","Diffuse follicle center lymphoma, lymph nodes of head, face, and neck",Diffuse follicle center lymphoma,9
C826,1,C8261,"Cutan folicl center lymphoma, nodes of head, face, and neck","Cutaneous follicle center lymphoma, lymph nodes of head, face, and neck",Cutaneous follicle center lymphoma,9
C828,1,C8281,"Oth types of foliclar lymph, nodes of head, face, and neck","Other types of follicular lymphoma, lymph nodes of head, face, and neck",Other types of follicular lymphoma,9
C829,1,C8291,"Follicular lymphoma, unsp, nodes of head, face, and neck","Follicular lymphoma, unspecified, lymph nodes of head, face, and neck","Follicular lymphoma, unspecified",9
C830,1,C8301,"Small cell B-cell lymphoma, nodes of head, face, and neck","Small cell B-cell lymphoma, lymph nodes of head, face, and neck",Small cell B-cell lymphoma,9
C831,1,C8311,"Mantle cell lymphoma, lymph nodes of head, face, and neck","Mantle cell lymphoma, lymph nodes of head, face, and neck",Mantle cell lymphoma,9
C833,1,C8331,"Diffuse large B-cell lymphoma, nodes of head, face, and neck","Diffuse large B-cell lymphoma, lymph nodes of head, face, and neck",Diffuse large B-cell lymphoma,9
C835,1,C8351,"Lymphoblastic lymphoma, nodes of head, face, and neck","Lymphoblastic (diffuse) lymphoma, lymph nodes of head, face, and neck",Lymphoblastic (diffuse) lymphoma,9
C837,1,C8371,"Burkitt lymphoma, lymph nodes of head, face, and neck","Burkitt lymphoma, lymph nodes of head, face, and neck",Burkitt lymphoma,9
C838,1,C8381,"Oth non-follic lymphoma, lymph nodes of head, face, and neck","Other non-follicular lymphoma, lymph nodes of head, face, and neck",Other non-follicular lymphoma,9
C839,1,C8391,"Non-follic lymphoma, unsp, nodes of head, face, and neck","Non-follicular (diffuse) lymphoma, unspecified, lymph nodes of head, face, and neck","Non-follicular (diffuse) lymphoma, unspecified",9
C840,1,C8401,"Mycosis fungoides, lymph nodes of head, face, and neck","Mycosis fungoides, lymph nodes of head, face, and neck",Mycosis fungoides,9
C841,1,C8411,"Sezary disease, lymph nodes of head, face, and neck","Sezary disease, lymph nodes of head, face, and neck",Sezary disease,9
C844,1,C8441,"Prph T-cell lymph, not class, nodes of head, face, and neck","Peripheral T-cell lymphoma, not classified, lymph nodes of head, face, and neck","Peripheral T-cell lymphoma, not classified",9
C846,1,C8461,"Anaplstc lg cell lymph, ALK-pos, nodes of head, face, and nk","Anaplastic large cell lymphoma, ALK-positive, lymph nodes of head, face, and neck","Anaplastic large cell lymphoma, ALK-positive",9
C847,1,C8471,"Anaplstc lg cell lymph, ALK-neg, nodes of head, face, and nk","Anaplastic large cell lymphoma, ALK-negative, lymph nodes of head, face, and neck","Anaplastic large cell lymphoma, ALK-negative",9
C84A,1,C84A1,"Cutan T-cell lymphoma, unsp nodes of head, face, and neck","Cutaneous T-cell lymphoma, unspecified lymph nodes of head, face, and neck","Cutaneous T-cell lymphoma, unspecified",9
C84Z,1,C84Z1,"Oth mature T/NK-cell lymph, nodes of head, face, and neck","Other mature T/NK-cell lymphomas, lymph nodes of head, face, and neck",Other mature T/NK-cell lymphomas,9
C849,1,C8491,"Mature T/NK-cell lymph, unsp, nodes of head, face, and neck","Mature T/NK-cell lymphomas, unspecified, lymph nodes of head, face, and neck","Mature T/NK-cell lymphomas, unspecified",9
C851,1,C8511,"Unsp B-cell lymphoma, lymph nodes of head, face, and neck","Unspecified B-cell lymphoma, lymph nodes of head, face, and neck",Unspecified B-cell lymphoma,9
C852,1,C8521,"Mediastnl large B-cell lymph, nodes of head, face, and neck","Mediastinal (thymic) large B-cell lymphoma, lymph nodes of head, face, and neck",Mediastinal (thymic) large B-cell lymphoma,9
C858,1,C8581,"Oth types of non-hodg lymph, nodes of head, face, and neck","Other specified types of non-Hodgkin lymphoma, lymph nodes of head, face, and neck",Other specified types of non-Hodgkin lymphoma,9
C859,1,C8591,"Non-Hodgkin lymphoma, unsp, nodes of head, face, and neck","Non-Hodgkin lymphoma, unspecified, lymph nodes of head, face, and neck","Non-Hodgkin lymphoma, unspecified",9
C86,1,C861,Hepatosplenic T-cell lymphoma,Hepatosplenic T-cell lymphoma,Other specified types of T/NK-cell lymphoma,9
C900,1,C9001,Multiple myeloma in remission,Multiple myeloma in remission,Multiple myeloma,9
C901,1,C9011,Plasma cell leukemia in remission,Plasma cell leukemia in remission,Plasma cell leukemia,9
C902,1,C9021,Extramedullary plasmacytoma in remission,Extramedullary plasmacytoma in remission,Extramedullary plasmacytoma,9
C903,1,C9031,Solitary plasmacytoma in remission,Solitary plasmacytoma in remission,Solitary plasmacytoma,9
C910,1,C9101,"Acute lymphoblastic leukemia, in remission","Acute lymphoblastic leukemia, in remission",Acute lymphoblastic leukemia [ALL],9
C911,1,C9111,Chronic lymphocytic leukemia of B-cell type in remission,Chronic lymphocytic leukemia of B-cell type in remission,Chronic lymphocytic leukemia of B-cell type,9
C913,1,C9131,"Prolymphocytic leukemia of B-cell type, in remission","Prolymphocytic leukemia of B-cell type, in remission",Prolymphocytic leukemia of B-cell type,9
C914,1,C9141,"Hairy cell leukemia, in remission","Hairy cell leukemia, in remission",Hairy cell leukemia,9
C915,1,C9151,"Adult T-cell lymphoma/leukemia (HTLV-1-assoc), in remission","Adult T-cell lymphoma/leukemia (HTLV-1-associated), in remission",Adult T-cell lymphoma/leukemia (HTLV-1-associated),9
C916,1,C9161,"Prolymphocytic leukemia of T-cell type, in remission","Prolymphocytic leukemia of T-cell type, in remission",Prolymphocytic leukemia of T-cell type,9
C91A,1,C91A1,"Mature B-cell leukemia Burkitt-type, in remission","Mature B-cell leukemia Burkitt-type, in remission",Mature B-cell leukemia Burkitt-type,9
C91Z,1,C91Z1,"Other lymphoid leukemia, in remission","Other lymphoid leukemia, in remission",Other lymphoid leukemia,9
C919,1,C9191,"Lymphoid leukemia, unspecified, in remission","Lymphoid leukemia, unspecified, in remission","Lymphoid leukemia, unspecified",9
C920,1,C9201,"Acute myeloblastic leukemia, in remission","Acute myeloblastic leukemia, in remission",Acute myeloblastic leukemia,9
C921,1,C9211,"Chronic myeloid leukemia, BCR/ABL-positive, in remission","Chronic myeloid leukemia, BCR/ABL-positive, in remission","Chronic myeloid leukemia, BCR/ABL-positive",9
C922,1,C9221,"Atypical chronic myeloid leukemia, BCR/ABL-neg, in remission","Atypical chronic myeloid leukemia, BCR/ABL-negative, in remission","Atypical chronic myeloid leukemia, BCR/ABL-negative",9
C923,1,C9231,"Myeloid sarcoma, in remission","Myeloid sarcoma, in remission",Myeloid sarcoma,9
C924,1,C9241,"Acute promyelocytic leukemia, in remission","Acute promyelocytic leukemia, in remission",Acute promyelocytic leukemia,9
C925,1,C9251,"Acute myelomonocytic leukemia, in remission","Acute myelomonocytic leukemia, in remission",Acute myelomonocytic leukemia,9
C926,1,C9261,Acute myeloid leukemia with 11q23-abnormality in remission,Acute myeloid leukemia with 11q23-abnormality in remission,Acute myeloid leukemia with 11q23-abnormality,9
C92A,1,C92A1,"Acute myeloid leukemia w multilin dysplasia, in remission","Acute myeloid leukemia with multilineage dysplasia, in remission",Acute myeloid leukemia with multilineage dysplasia,9
C92Z,1,C92Z1,"Other myeloid leukemia, in remission","Other myeloid leukemia, in remission",Other myeloid leukemia,9
C929,1,C9291,"Myeloid leukemia, unspecified in remission","Myeloid leukemia, unspecified in remission","Myeloid leukemia, unspecified",9
C930,1,C9301,"Acute monoblastic/monocytic leukemia, in remission","Acute monoblastic/monocytic leukemia, in remission",Acute monoblastic/monocytic leukemia,9
C931,1,C9311,"Chronic myelomonocytic leukemia, in remission","Chronic myelomonocytic leukemia, in remission",Chronic myelomonocytic leukemia,9
C933,1,C9331,"Juvenile myelomonocytic leukemia, in remission","Juvenile myelomonocytic leukemia, in remission",Juvenile myelomonocytic leukemia,9
C93Z,1,C93Z1,"Other monocytic leukemia, in remission","Other monocytic leukemia, in remission",Other monocytic leukemia,9
C939,1,C9391,"Monocytic leukemia, unspecified in remission","Monocytic leukemia, unspecified in remission","Monocytic leukemia, unspecified",9
C940,1,C9401,"Acute erythroid leukemia, in remission","Acute erythroid leukemia, in remission",Acute erythroid leukemia,9
C942,1,C9421,"Acute megakaryoblastic leukemia, in remission","Acute megakaryoblastic leukemia, in remission",Acute megakaryoblastic leukemia,9
C943,1,C9431,"Mast cell leukemia, in remission","Mast cell leukemia, in remission",Mast cell leukemia,9
C944,1,C9441,"Acute panmyelosis with myelofibrosis, in remission","Acute panmyelosis with myelofibrosis, in remission",Acute panmyelosis with myelofibrosis,9
C948,1,C9481,"Other specified leukemias, in remission","Other specified leukemias, in remission",Other specified leukemias,9
C950,1,C9501,"Acute leukemia of unspecified cell type, in remission","Acute leukemia of unspecified cell type, in remission",Acute leukemia of unspecified cell type,9
C951,1,C9511,"Chronic leukemia of unspecified cell type, in remission","Chronic leukemia of unspecified cell type, in remission",Chronic leukemia of unspecified cell type,9
C959,1,C9591,"Leukemia, unspecified, in remission","Leukemia, unspecified, in remission","Leukemia, unspecified",9
C962,1,C9621,Aggressive systemic mastocytosis,Aggressive systemic mastocytosis,Malignant mast cell neoplasm,9
D000,1,D0001,Carcinoma in situ of labial mucosa and vermilion border,Carcinoma in situ of labial mucosa and vermilion border,"Carcinoma in situ of lip, oral cavity and pharynx",9
D01,1,D011,Carcinoma in situ of rectosigmoid junction,Carcinoma in situ of rectosigmoid junction,Carcinoma in situ of other and unspecified digestive organs,9
D02,1,D021,Carcinoma in situ of trachea,Carcinoma in situ of trachea,Carcinoma in situ of middle ear and respiratory system,9
D022,1,D0221,Carcinoma in situ of right bronchus and lung,Carcinoma in situ of right bronchus and lung,Carcinoma in situ of bronchus and lung,9
D031,1,D0311,"Melanoma in situ of right eyelid, including canthus","Melanoma in situ of right eyelid, including canthus","Melanoma in situ of eyelid, including canthus",9
D032,1,D0321,Melanoma in situ of right ear and external auricular canal,Melanoma in situ of right ear and external auricular canal,Melanoma in situ of ear and external auricular canal,9
D035,1,D0351,Melanoma in situ of anal skin,Melanoma in situ of anal skin,Melanoma in situ of trunk,9
D036,1,D0361,"Melanoma in situ of right upper limb, including shoulder","Melanoma in situ of right upper limb, including shoulder","Melanoma in situ of upper limb, including shoulder",9
D037,1,D0371,"Melanoma in situ of right lower limb, including hip","Melanoma in situ of right lower limb, including hip","Melanoma in situ of lower limb, including hip",9
D041,1,D0411,"Carcinoma in situ of skin of right eyelid, including canthus","Carcinoma in situ of skin of right eyelid, including canthus","Carcinoma in situ of skin of eyelid, including canthus",9
D042,1,D0421,Ca in situ skin of right ear and external auricular canal,Carcinoma in situ of skin of right ear and external auricular canal,Carcinoma in situ of skin of ear and external auricular canal,9
D046,1,D0461,"Ca in situ skin of right upper limb, including shoulder","Carcinoma in situ of skin of right upper limb, including shoulder","Carcinoma in situ of skin of upper limb, including shoulder",9
D047,1,D0471,"Carcinoma in situ of skin of right lower limb, including hip","Carcinoma in situ of skin of right lower limb, including hip","Carcinoma in situ of skin of lower limb, including hip",9
D050,1,D0501,Lobular carcinoma in situ of right breast,Lobular carcinoma in situ of right breast,Lobular carcinoma in situ of breast,9
D051,1,D0511,Intraductal carcinoma in situ of right breast,Intraductal carcinoma in situ of right breast,Intraductal carcinoma in situ of breast,9
D058,1,D0581,Other specified type of carcinoma in situ of right breast,Other specified type of carcinoma in situ of right breast,Other specified type of carcinoma in situ of breast,9
D059,1,D0591,Unspecified type of carcinoma in situ of right breast,Unspecified type of carcinoma in situ of right breast,Unspecified type of carcinoma in situ of breast,9
D06,1,D061,Carcinoma in situ of exocervix,Carcinoma in situ of exocervix,Carcinoma in situ of cervix uteri,9
D07,1,D071,Carcinoma in situ of vulva,Carcinoma in situ of vulva,Carcinoma in situ of other and unspecified genital organs,9
D076,1,D0761,Carcinoma in situ of scrotum,Carcinoma in situ of scrotum,Carcinoma in situ of other and unspecified male genital organs,9
D092,1,D0921,Carcinoma in situ of right eye,Carcinoma in situ of right eye,Carcinoma in situ of eye,9
D10,1,D101,Benign neoplasm of tongue,Benign neoplasm of tongue,Benign neoplasm of mouth and pharynx,9
D12,1,D121,Benign neoplasm of appendix,Benign neoplasm of appendix,"Benign neoplasm of colon, rectum, anus and anal canal",9
D13,1,D131,Benign neoplasm of stomach,Benign neoplasm of stomach,Benign neoplasm of other and ill-defined parts of digestive system,9
D14,1,D141,Benign neoplasm of larynx,Benign neoplasm of larynx,Benign neoplasm of middle ear and respiratory system,9
D143,1,D1431,Benign neoplasm of right bronchus and lung,Benign neoplasm of right bronchus and lung,Benign neoplasm of bronchus and lung,9
D15,1,D151,Benign neoplasm of heart,Benign neoplasm of heart,Benign neoplasm of other and unspecified intrathoracic organs,9
D160,1,D1601,Benign neoplm of scapula and long bones of right upper limb,Benign neoplasm of scapula and long bones of right upper limb,Benign neoplasm of scapula and long bones of upper limb,9
D161,1,D1611,Benign neoplasm of short bones of right upper limb,Benign neoplasm of short bones of right upper limb,Benign neoplasm of short bones of upper limb,9
D162,1,D1621,Benign neoplasm of long bones of right lower limb,Benign neoplasm of long bones of right lower limb,Benign neoplasm of long bones of lower limb,9
D163,1,D1631,Benign neoplasm of short bones of right lower limb,Benign neoplasm of short bones of right lower limb,Benign neoplasm of short bones of lower limb,9
D17,1,D171,"Benign lipomatous neoplasm of skin, subcu of trunk",Benign lipomatous neoplasm of skin and subcutaneous tissue of trunk,Benign lipomatous neoplasm,9
D172,1,D1721,"Benign lipomatous neoplasm of skin, subcu of right arm",Benign lipomatous neoplasm of skin and subcutaneous tissue of right arm,Benign lipomatous neoplasm of skin and subcutaneous tissue of limb,9
D177,1,D1771,Benign lipomatous neoplasm of kidney,Benign lipomatous neoplasm of kidney,Benign lipomatous neoplasm of other sites,9
D180,1,D1801,Hemangioma of skin and subcutaneous tissue,Hemangioma of skin and subcutaneous tissue,Hemangioma,9
D19,1,D191,Benign neoplasm of mesothelial tissue of peritoneum,Benign neoplasm of mesothelial tissue of peritoneum,Benign neoplasm of mesothelial tissue,9
D20,1,D201,Benign neoplasm of soft tissue of peritoneum,Benign neoplasm of soft tissue of peritoneum,Benign neoplasm of soft tissue of retroperitoneum and peritoneum,9
D211,1,D2111,"Ben neoplm of connctv/soft tiss of r upper limb, inc shldr","Benign neoplasm of connective and other soft tissue of right upper limb, including shoulder","Benign neoplasm of connective and other soft tissue of upper limb, including shoulder",9
D212,1,D2121,"Ben neoplm of connctv/soft tiss of right lower limb, inc hip","Benign neoplasm of connective and other soft tissue of right lower limb, including hip","Benign neoplasm of connective and other soft tissue of lower limb, including hip",9
D221,1,D2211,"Melanocytic nevi of right eyelid, including canthus","Melanocytic nevi of right eyelid, including canthus","Melanocytic nevi of eyelid, including canthus",9
D222,1,D2221,Melanocytic nevi of right ear and external auricular canal,Melanocytic nevi of right ear and external auricular canal,Melanocytic nevi of ear and external auricular canal,9
D226,1,D2261,"Melanocytic nevi of right upper limb, including shoulder","Melanocytic nevi of right upper limb, including shoulder","Melanocytic nevi of upper limb, including shoulder",9
D227,1,D2271,"Melanocytic nevi of right lower limb, including hip","Melanocytic nevi of right lower limb, including hip","Melanocytic nevi of lower limb, including hip",9
D231,1,D2311,"Oth benign neoplasm skin/ right eyelid, including canthus","Other benign neoplasm of skin of right eyelid, including canthus","Other benign neoplasm of skin of eyelid, including canthus",9
D232,1,D2321,Oth benign neoplasm skin/ right ear and external auric canal,Other benign neoplasm of skin of right ear and external auricular canal,Other benign neoplasm of skin of ear and external auricular canal,9
D236,1,D2361,"Oth benign neoplasm skin/ right upper limb, inc shoulder","Other benign neoplasm of skin of right upper limb, including shoulder","Other benign neoplasm of skin of upper limb, including shoulder",9
D237,1,D2371,"Oth benign neoplasm skin/ right lower limb, including hip","Other benign neoplasm of skin of right lower limb, including hip","Other benign neoplasm of skin of lower limb, including hip",9
D24,1,D241,Benign neoplasm of right breast,Benign neoplasm of right breast,Benign neoplasm of breast,9
D25,1,D251,Intramural leiomyoma of uterus,Intramural leiomyoma of uterus,Leiomyoma of uterus,9
D26,1,D261,Other benign neoplasm of corpus uteri,Other benign neoplasm of corpus uteri,Other benign neoplasms of uterus,9
D27,1,D271,Benign neoplasm of left ovary,Benign neoplasm of left ovary,Benign neoplasm of ovary,9
D28,1,D281,Benign neoplasm of vagina,Benign neoplasm of vagina,Benign neoplasm of other and unspecified female genital organs,9
D29,1,D291,Benign neoplasm of prostate,Benign neoplasm of prostate,Benign neoplasm of male genital organs,9
D292,1,D2921,Benign neoplasm of right testis,Benign neoplasm of right testis,Benign neoplasm of testis,9
D293,1,D2931,Benign neoplasm of right epididymis,Benign neoplasm of right epididymis,Benign neoplasm of epididymis,9
D300,1,D3001,Benign neoplasm of right kidney,Benign neoplasm of right kidney,Benign neoplasm of kidney,9
D301,1,D3011,Benign neoplasm of right renal pelvis,Benign neoplasm of right renal pelvis,Benign neoplasm of renal pelvis,9
D302,1,D3021,Benign neoplasm of right ureter,Benign neoplasm of right ureter,Benign neoplasm of ureter,9
D310,1,D3101,Benign neoplasm of right conjunctiva,Benign neoplasm of right conjunctiva,Benign neoplasm of conjunctiva,9
D311,1,D3111,Benign neoplasm of right cornea,Benign neoplasm of right cornea,Benign neoplasm of cornea,9
D312,1,D3121,Benign neoplasm of right retina,Benign neoplasm of right retina,Benign neoplasm of retina,9
D313,1,D3131,Benign neoplasm of right choroid,Benign neoplasm of right choroid,Benign neoplasm of choroid,9
D314,1,D3141,Benign neoplasm of right ciliary body,Benign neoplasm of right ciliary body,Benign neoplasm of ciliary body,9
D315,1,D3151,Benign neoplasm of right lacrimal gland and duct,Benign neoplasm of right lacrimal gland and duct,Benign neoplasm of lacrimal gland and duct,9
D316,1,D3161,Benign neoplasm of unspecified site of right orbit,Benign neoplasm of unspecified site of right orbit,Benign neoplasm of unspecified site of orbit,9
D319,1,D3191,Benign neoplasm of unspecified part of right eye,Benign neoplasm of unspecified part of right eye,Benign neoplasm of unspecified part of eye,9
D32,1,D321,Benign neoplasm of spinal meninges,Benign neoplasm of spinal meninges,Benign neoplasm of meninges,9
D33,1,D331,"Benign neoplasm of brain, infratentorial","Benign neoplasm of brain, infratentorial",Benign neoplasm of brain and other parts of central nervous system,9
D350,1,D3501,Benign neoplasm of right adrenal gland,Benign neoplasm of right adrenal gland,Benign neoplasm of adrenal gland,9
D361,1,D3611,Ben neoplm of prph nerves and autonm nrv sys of face/hed/nk,"Benign neoplasm of peripheral nerves and autonomic nervous system of face, head, and neck",Benign neoplasm of peripheral nerves and autonomic nervous system,9
D3A01,1,D3A011,Benign carcinoid tumor of the jejunum,Benign carcinoid tumor of the jejunum,Benign carcinoid tumors of the small intestine,9
D3A02,1,D3A021,Benign carcinoid tumor of the cecum,Benign carcinoid tumor of the cecum,"Benign carcinoid tumors of the appendix, large intestine, and rectum",9
D3A09,1,D3A091,Benign carcinoid tumor of the thymus,Benign carcinoid tumor of the thymus,Benign carcinoid tumors of other sites,9
D370,1,D3701,Neoplasm of uncertain behavior of lip,Neoplasm of uncertain behavior of lip,"Neoplasm of uncertain behavior of lip, oral cavity and pharynx",9
D3703,1,D37031,Neoplasm of uncrt behavior of the sublingual salivary gland,Neoplasm of uncertain behavior of the sublingual salivary glands,Neoplasm of uncertain behavior of the major salivary glands,9
D38,1,D381,"Neoplasm of uncertain behavior of trachea, bronchus and lung","Neoplasm of uncertain behavior of trachea, bronchus and lung",Neoplasm of uncertain behavior of middle ear and respiratory and intrathoracic organs,9
D391,1,D3911,Neoplasm of uncertain behavior of right ovary,Neoplasm of uncertain behavior of right ovary,Neoplasm of uncertain behavior of ovary,9
D401,1,D4011,Neoplasm of uncertain behavior of right testis,Neoplasm of uncertain behavior of right testis,Neoplasm of uncertain behavior of testis,9
D410,1,D4101,Neoplasm of uncertain behavior of right kidney,Neoplasm of uncertain behavior of right kidney,Neoplasm of uncertain behavior of kidney,9
D411,1,D4111,Neoplasm of uncertain behavior of right renal pelvis,Neoplasm of uncertain behavior of right renal pelvis,Neoplasm of uncertain behavior of renal pelvis,9
D412,1,D4121,Neoplasm of uncertain behavior of right ureter,Neoplasm of uncertain behavior of right ureter,Neoplasm of uncertain behavior of ureter,9
D42,1,D421,Neoplasm of uncertain behavior of spinal meninges,Neoplasm of uncertain behavior of spinal meninges,Neoplasm of uncertain behavior of meninges,9
D43,1,D431,"Neoplasm of uncertain behavior of brain, infratentorial","Neoplasm of uncertain behavior of brain, infratentorial",Neoplasm of uncertain behavior of brain and central nervous system,9
D441,1,D4411,Neoplasm of uncertain behavior of right adrenal gland,Neoplasm of uncertain behavior of right adrenal gland,Neoplasm of uncertain behavior of adrenal gland,9
D46,1,D461,Refractory anemia with ring sideroblasts,Refractory anemia with ring sideroblasts,Myelodysplastic syndromes,9
D462,1,D4621,Refractory anemia with excess of blasts 1,Refractory anemia with excess of blasts 1,Refractory anemia with excess of blasts [RAEB],9
D470,1,D4701,Cutaneous mastocytosis,Cutaneous mastocytosis,Mast cell neoplasms of uncertain behavior,9
D47Z,1,D47Z1,Post-transplant lymphoproliferative disorder (PTLD),Post-transplant lymphoproliferative disorder (PTLD),"Other specified neoplasms of uncertain behavior of lymphoid, hematopoietic and related tissue",9
D48,1,D481,Neoplasm of uncertain behavior of connctv/soft tiss,Neoplasm of uncertain behavior of connective and other soft tissue,Neoplasm of uncertain behavior of other and unspecified sites,9
D486,1,D4861,Neoplasm of uncertain behavior of right breast,Neoplasm of uncertain behavior of right breast,Neoplasm of uncertain behavior of breast,9
D49,1,D491,Neoplasm of unspecified behavior of respiratory system,Neoplasm of unspecified behavior of respiratory system,Neoplasms of unspecified behavior,9
D4951,1,D49511,Neoplasm of unspecified behavior of right kidney,Neoplasm of unspecified behavior of right kidney,Neoplasm of unspecified behavior of kidney,9
D498,1,D4981,Neoplasm of unspecified behavior of retina and choroid,Neoplasm of unspecified behavior of retina and choroid,Neoplasm of unspecified behavior of other specified sites,9
D50,1,D501,Sideropenic dysphagia,Sideropenic dysphagia,Iron deficiency anemia,9
D51,1,D511,Vit B12 defic anemia d/t slctv vit B12 malabsorp w protein,Vitamin B12 deficiency anemia due to selective vitamin B12 malabsorption with proteinuria,Vitamin B12 deficiency anemia,9
D52,1,D521,Drug-induced folate deficiency anemia,Drug-induced folate deficiency anemia,Folate deficiency anemia,9
D53,1,D531,"Other megaloblastic anemias, not elsewhere classified","Other megaloblastic anemias, not elsewhere classified",Other nutritional anemias,9
D55,1,D551,Anemia due to other disorders of glutathione metabolism,Anemia due to other disorders of glutathione metabolism,Anemia due to enzyme disorders,9
D56,1,D561,Beta thalassemia,Beta thalassemia,Thalassemia,9
D570,1,D5701,Hb-SS disease with acute chest syndrome,Hb-SS disease with acute chest syndrome,Hb-SS disease with crisis,9
D5721,1,D57211,Sickle-cell/Hb-C disease with acute chest syndrome,Sickle-cell/Hb-C disease with acute chest syndrome,Sickle-cell/Hb-C disease with crisis,9
D5741,1,D57411,Sickle-cell thalassemia with acute chest syndrome,Sickle-cell thalassemia with acute chest syndrome,Sickle-cell thalassemia with crisis,9
D5781,1,D57811,Other sickle-cell disorders with acute chest syndrome,Other sickle-cell disorders with acute chest syndrome,Other sickle-cell disorders with crisis,9
D58,1,D581,Hereditary elliptocytosis,Hereditary elliptocytosis,Other hereditary hemolytic anemias,9
D59,1,D591,Other autoimmune hemolytic anemias,Other autoimmune hemolytic anemias,Acquired hemolytic anemia,9
D60,1,D601,Transient acquired pure red cell aplasia,Transient acquired pure red cell aplasia,Acquired pure red cell aplasia [erythroblastopenia],9
D610,1,D6101,Constitutional (pure) red blood cell aplasia,Constitutional (pure) red blood cell aplasia,Constitutional aplastic anemia,9
D6181,1,D61811,Other drug-induced pancytopenia,Other drug-induced pancytopenia,Pancytopenia,9
D63,1,D631,Anemia in chronic kidney disease,Anemia in chronic kidney disease,Anemia in chronic diseases classified elsewhere,9
D64,1,D641,Secondary sideroblastic anemia due to disease,Secondary sideroblastic anemia due to disease,Other anemias,9
D648,1,D6481,Anemia due to antineoplastic chemotherapy,Anemia due to antineoplastic chemotherapy,Other specified anemias,9
D68,1,D681,Hereditary factor XI deficiency,Hereditary factor XI deficiency,Other coagulation defects,9
D6831,1,D68311,Acquired hemophilia,Acquired hemophilia,"Hemorrhagic disorder due to intrinsic circulating anticoagulants, antibodies, or inhibitors",9
D685,1,D6851,Activated protein C resistance,Activated protein C resistance,Primary thrombophilia,9
D686,1,D6861,Antiphospholipid syndrome,Antiphospholipid syndrome,Other thrombophilia,9
D69,1,D691,Qualitative platelet defects,Qualitative platelet defects,Purpura and other hemorrhagic conditions,9
D694,1,D6941,Evans syndrome,Evans syndrome,Other primary thrombocytopenia,9
D695,1,D6951,Posttransfusion purpura,Posttransfusion purpura,Secondary thrombocytopenia,9
D70,1,D701,Agranulocytosis secondary to cancer chemotherapy,Agranulocytosis secondary to cancer chemotherapy,Neutropenia,9
D72,1,D721,Eosinophilia,Eosinophilia,Other disorders of white blood cells,9
D7282,1,D72821,Monocytosis (symptomatic),Monocytosis (symptomatic),Elevated white blood cell count,9
D73,1,D731,Hypersplenism,Hypersplenism,Diseases of spleen,9
D75,1,D751,Secondary polycythemia,Secondary polycythemia,Other and unspecified diseases of blood and blood-forming organs,9
D758,1,D7581,Myelofibrosis,Myelofibrosis,Other specified diseases of blood and blood-forming organs,9
D76,1,D761,Hemophagocytic lymphohistiocytosis,Hemophagocytic lymphohistiocytosis,Other specified diseases with participation of lymphoreticular and reticulohistiocytic tissue,9
D780,1,D7801,Intraop hemor/hemtom of the spleen comp a proc on the spleen,Intraoperative hemorrhage and hematoma of the spleen complicating a procedure on the spleen,Intraoperative hemorrhage and hematoma of the spleen complicating a procedure,9
D781,1,D7811,Accidental pnctr & lac of the spleen dur proc on the spleen,Accidental puncture and laceration of the spleen during a procedure on the spleen,Accidental puncture and laceration of the spleen during a procedure,9
D782,1,D7821,Postprocedural hemorrhage of the spleen fol proc on spleen,Postprocedural hemorrhage of the spleen following a procedure on the spleen,Postprocedural hemorrhage of the spleen following a procedure,9
D783,1,D7831,Postprocedural hematoma of the spleen fol proc on spleen,Postprocedural hematoma of the spleen following a procedure on the spleen,Postprocedural hematoma and seroma of the spleen following a procedure,9
D788,1,D7881,Other intraoperative complications of the spleen,Other intraoperative complications of the spleen,Other intraoperative and postprocedural complications of the spleen,9
D80,1,D801,Nonfamilial hypogammaglobulinemia,Nonfamilial hypogammaglobulinemia,Immunodeficiency with predominantly antibody defects,9
D81,1,D811,Severe combined immunodeficiency w low T- and B-cell numbers,Severe combined immunodeficiency [SCID] with low T- and B-cell numbers,Combined immunodeficiencies,9
D82,1,D821,Di George's syndrome,Di George's syndrome,Immunodeficiency associated with other major defects,9
D83,1,D831,Com variab immunodef w predom immunoreg T-cell disorders,Common variable immunodeficiency with predominant immunoregulatory T-cell disorders,Common variable immunodeficiency,9
D84,1,D841,Defects in the complement system,Defects in the complement system,Other immunodeficiencies,9
D86,1,D861,Sarcoidosis of lymph nodes,Sarcoidosis of lymph nodes,Sarcoidosis,9
D868,1,D8681,Sarcoid meningitis,Sarcoid meningitis,Sarcoidosis of other sites,9
D89,1,D891,Cryoglobulinemia,Cryoglobulinemia,"Other disorders involving the immune mechanism, not elsewhere classified",9
D894,1,D8941,Monoclonal mast cell activation syndrome,Monoclonal mast cell activation syndrome,Mast cell activation syndrome and related disorders,9
D8981,1,D89811,Chronic graft-versus-host disease,Chronic graft-versus-host disease,Graft-versus-host disease,9
E00,1,E001,"Congenital iodine-deficiency syndrome, myxedematous type","Congenital iodine-deficiency syndrome, myxedematous type",Congenital iodine-deficiency syndrome,9
E01,1,E011,Iodine-deficiency related multinodular (endemic) goiter,Iodine-deficiency related multinodular (endemic) goiter,Iodine-deficiency related thyroid disorders and allied conditions,9
E03,1,E031,Congenital hypothyroidism without goiter,Congenital hypothyroidism without goiter,Other hypothyroidism,9
E04,1,E041,Nontoxic single thyroid nodule,Nontoxic single thyroid nodule,Other nontoxic goiter,9
E050,1,E0501,Thyrotoxicosis w diffuse goiter w thyrotoxic crisis or storm,Thyrotoxicosis with diffuse goiter with thyrotoxic crisis or storm,Thyrotoxicosis with diffuse goiter,9
E051,1,E0511,Thyrotxcosis w toxic single thyroid nodule w thyrotxc crisis,Thyrotoxicosis with toxic single thyroid nodule with thyrotoxic crisis or storm,Thyrotoxicosis with toxic single thyroid nodule,9
E052,1,E0521,Thyrotxcosis w toxic multinodular goiter w thyrotoxic crisis,Thyrotoxicosis with toxic multinodular goiter with thyrotoxic crisis or storm,Thyrotoxicosis with toxic multinodular goiter,9
E053,1,E0531,Thyrotxcosis from ectopic thyroid tissue w thyrotoxic crisis,Thyrotoxicosis from ectopic thyroid tissue with thyrotoxic crisis or storm,Thyrotoxicosis from ectopic thyroid tissue,9
E054,1,E0541,Thyrotoxicosis factitia with thyrotoxic crisis or storm,Thyrotoxicosis factitia with thyrotoxic crisis or storm,Thyrotoxicosis factitia,9
E058,1,E0581,Other thyrotoxicosis with thyrotoxic crisis or storm,Other thyrotoxicosis with thyrotoxic crisis or storm,Other thyrotoxicosis,9
E059,1,E0591,"Thyrotoxicosis, unspecified with thyrotoxic crisis or storm","Thyrotoxicosis, unspecified with thyrotoxic crisis or storm","Thyrotoxicosis, unspecified",9
E06,1,E061,Subacute thyroiditis,Subacute thyroiditis,Thyroiditis,9
E07,1,E071,Dyshormogenetic goiter,Dyshormogenetic goiter,Other disorders of thyroid,9
E078,1,E0781,Sick-euthyroid syndrome,Sick-euthyroid syndrome,Other specified disorders of thyroid,9
E080,1,E0801,Diabetes due to underlying condition w hyprosm w coma,Diabetes mellitus due to underlying condition with hyperosmolarity with coma,Diabetes mellitus due to underlying condition with hyperosmolarity,9
E081,1,E0811,Diabetes due to underlying condition w ketoacidosis w coma,Diabetes mellitus due to underlying condition with ketoacidosis with coma,Diabetes mellitus due to underlying condition with ketoacidosis,9
E082,1,E0821,Diabetes due to underlying condition w diabetic nephropathy,Diabetes mellitus due to underlying condition with diabetic nephropathy,Diabetes mellitus due to underlying condition with kidney complications,9
E0831,1,E08311,Diab due to undrl cond w unsp diabetic rtnop w macular edema,Diabetes mellitus due to underlying condition with unspecified diabetic retinopathy with macular edema,Diabetes mellitus due to underlying condition with unspecified diabetic retinopathy,9
E08321,1,E083211,"Diabetes with mild nonp rtnop with macular edema, right eye","Diabetes mellitus due to underlying condition with mild nonproliferative diabetic retinopathy with macular edema, right eye",Diabetes mellitus due to underlying condition with mild nonproliferative diabetic retinopathy with macular edema,9
E08329,1,E083291,"Diabetes with mild nonp rtnop without macular edema, r eye","Diabetes mellitus due to underlying condition with mild nonproliferative diabetic retinopathy without macular edema, right eye",Diabetes mellitus due to underlying condition with mild nonproliferative diabetic retinopathy without macular edema,9
E08331,1,E083311,"Diabetes with moderate nonp rtnop with macular edema, r eye","Diabetes mellitus due to underlying condition with moderate nonproliferative diabetic retinopathy with macular edema, right eye",Diabetes mellitus due to underlying condition with moderate nonproliferative diabetic retinopathy with macular edema,9
E08339,1,E083391,"Diab with moderate nonp rtnop without macular edema, r eye","Diabetes mellitus due to underlying condition with moderate nonproliferative diabetic retinopathy without macular edema, right eye",Diabetes mellitus due to underlying condition with moderate nonproliferative diabetic retinopathy without macular edema,9
E08341,1,E083411,"Diabetes with severe nonp rtnop with macular edema, r eye","Diabetes mellitus due to underlying condition with severe nonproliferative diabetic retinopathy with macular edema, right eye",Diabetes mellitus due to underlying condition with severe nonproliferative diabetic retinopathy with macular edema,9
E08349,1,E083491,"Diabetes with severe nonp rtnop without macular edema, r eye","Diabetes mellitus due to underlying condition with severe nonproliferative diabetic retinopathy without macular edema, right eye",Diabetes mellitus due to underlying condition with severe nonproliferative diabetic retinopathy without macular edema,9
E08351,1,E083511,"Diab with prolif diabetic rtnop with macular edema, r eye","Diabetes mellitus due to underlying condition with proliferative diabetic retinopathy with macular edema, right eye",Diabetes mellitus due to underlying condition with proliferative diabetic retinopathy with macular edema,9
E08352,1,E083521,"Diab with prolif diab rtnop with trctn dtch macula, r eye","Diabetes mellitus due to underlying condition with proliferative diabetic retinopathy with traction retinal detachment involving the macula, right eye",Diabetes mellitus due to underlying condition with proliferative diabetic retinopathy with traction retinal detachment involving the macula,9
E08353,1,E083531,"Diab with prolif diab rtnop with trctn dtch n-mcla, r eye","Diabetes mellitus due to underlying condition with proliferative diabetic retinopathy with traction retinal detachment not involving the macula, right eye",Diabetes mellitus due to underlying condition with proliferative diabetic retinopathy with traction retinal detachment not involving the macula,9
E08354,1,E083541,"Diabetes with prolif diabetic rtnop with comb detach, r eye","Diabetes mellitus due to underlying condition with proliferative diabetic retinopathy with combined traction retinal detachment and rhegmatogenous retinal detachment, right eye",Diabetes mellitus due to underlying condition with proliferative diabetic retinopathy with combined traction retinal detachment and rhegmatogenous retinal detachment,9
E08355,1,E083551,"Diabetes with stable prolif diabetic retinopathy, right eye","Diabetes mellitus due to underlying condition with stable proliferative diabetic retinopathy, right eye",Diabetes mellitus due to underlying condition with stable proliferative diabetic retinopathy,9
E08359,1,E083591,"Diab with prolif diabetic rtnop without macular edema, r eye","Diabetes mellitus due to underlying condition with proliferative diabetic retinopathy without macular edema, right eye",Diabetes mellitus due to underlying condition with proliferative diabetic retinopathy without macular edema,9
E084,1,E0841,Diabetes due to undrl condition w diabetic mononeuropathy,Diabetes mellitus due to underlying condition with diabetic mononeuropathy,Diabetes mellitus due to underlying condition with neurological complications,9
E085,1,E0851,Diab due to undrl cond w diab prph angiopath w/o gangrene,Diabetes mellitus due to underlying condition with diabetic peripheral angiopathy without gangrene,Diabetes mellitus due to underlying condition with circulatory complications,9
E0862,1,E08621,Diabetes mellitus due to underlying condition w foot ulcer,Diabetes mellitus due to underlying condition with foot ulcer,Diabetes mellitus due to underlying condition with skin complications,9
E0864,1,E08641,Diabetes due to underlying condition w hypoglycemia w coma,Diabetes mellitus due to underlying condition with hypoglycemia with coma,Diabetes mellitus due to underlying condition with hypoglycemia,9
E090,1,E0901,Drug/chem diabetes mellitus w hyperosmolarity w coma,Drug or chemical induced diabetes mellitus with hyperosmolarity with coma,Drug or chemical induced diabetes mellitus with hyperosmolarity,9
E091,1,E0911,Drug/chem diabetes mellitus w ketoacidosis w coma,Drug or chemical induced diabetes mellitus with ketoacidosis with coma,Drug or chemical induced diabetes mellitus with ketoacidosis,9
E092,1,E0921,Drug/chem diabetes mellitus w diabetic nephropathy,Drug or chemical induced diabetes mellitus with diabetic nephropathy,Drug or chemical induced diabetes mellitus with kidney complications,9
E0931,1,E09311,Drug/chem diabetes w unsp diabetic rtnop w macular edema,Drug or chemical induced diabetes mellitus with unspecified diabetic retinopathy with macular edema,Drug or chemical induced diabetes mellitus with unspecified diabetic retinopathy,9
E09321,1,E093211,"Drug/chem diab with mild nonp rtnop with mclr edema, r eye","Drug or chemical induced diabetes mellitus with mild nonproliferative diabetic retinopathy with macular edema, right eye",Drug or chemical induced diabetes mellitus with mild nonproliferative diabetic retinopathy with macular edema,9
E09329,1,E093291,"Drug/chem diab with mild nonp rtnop w/o mclr edema, r eye","Drug or chemical induced diabetes mellitus with mild nonproliferative diabetic retinopathy without macular edema, right eye",Drug or chemical induced diabetes mellitus with mild nonproliferative diabetic retinopathy without macular edema,9
E09331,1,E093311,"Drug/chem diab with mod nonp rtnop with macular edema, r eye","Drug or chemical induced diabetes mellitus with moderate nonproliferative diabetic retinopathy with macular edema, right eye",Drug or chemical induced diabetes mellitus with moderate nonproliferative diabetic retinopathy with macular edema,9
E09339,1,E093391,"Drug/chem diab with mod nonp rtnop without mclr edema, r eye","Drug or chemical induced diabetes mellitus with moderate nonproliferative diabetic retinopathy without macular edema, right eye",Drug or chemical induced diabetes mellitus with moderate nonproliferative diabetic retinopathy without macular edema,9
E09341,1,E093411,"Drug/chem diab with severe nonp rtnop with mclr edema, r eye","Drug or chemical induced diabetes mellitus with severe nonproliferative diabetic retinopathy with macular edema, right eye",Drug or chemical induced diabetes mellitus with severe nonproliferative diabetic retinopathy with macular edema,9
E09349,1,E093491,"Drug/chem diab with severe nonp rtnop w/o mclr edema, r eye","Drug or chemical induced diabetes mellitus with severe nonproliferative diabetic retinopathy without macular edema, right eye",Drug or chemical induced diabetes mellitus with severe nonproliferative diabetic retinopathy without macular edema,9
E09351,1,E093511,"Drug/chem diab with prolif diab rtnop with mclr edema, r eye","Drug or chemical induced diabetes mellitus with proliferative diabetic retinopathy with macular edema, right eye",Drug or chemical induced diabetes mellitus with proliferative diabetic retinopathy with macular edema,9
E1062,1,E10621,Type 1 diabetes mellitus with foot ulcer,Type 1 diabetes mellitus with foot ulcer,Type 1 diabetes mellitus with skin complications,9
E09352,1,E093521,"Drug/chem diab w prolif diab rtnop w trctn dtch macula,r eye","Drug or chemical induced diabetes mellitus with proliferative diabetic retinopathy with traction retinal detachment involving the macula, right eye",Drug or chemical induced diabetes mellitus with proliferative diabetic retinopathy with traction retinal detachment involving the macula,9
E09353,1,E093531,"Drug/chem diab w prolif diab rtnop w trctn dtch n-mcla,r eye","Drug or chemical induced diabetes mellitus with proliferative diabetic retinopathy with traction retinal detachment not involving the macula, right eye",Drug or chemical induced diabetes mellitus with proliferative diabetic retinopathy with traction retinal detachment not involving the macula,9
E09354,1,E093541,"Drug/chem diab w prolif diab rtnop with comb detach, r eye","Drug or chemical induced diabetes mellitus with proliferative diabetic retinopathy with combined traction retinal detachment and rhegmatogenous retinal detachment, right eye",Drug or chemical induced diabetes mellitus with proliferative diabetic retinopathy with combined traction retinal detachment and rhegmatogenous retinal detachment,9
E09355,1,E093551,"Drug/chem diabetes with stable prolif diabetic rtnop, r eye","Drug or chemical induced diabetes mellitus with stable proliferative diabetic retinopathy, right eye",Drug or chemical induced diabetes mellitus with stable proliferative diabetic retinopathy,9
E09359,1,E093591,"Drug/chem diab with prolif diab rtnop w/o mclr edema, r eye","Drug or chemical induced diabetes mellitus with proliferative diabetic retinopathy without macular edema, right eye",Drug or chemical induced diabetes mellitus with proliferative diabetic retinopathy without macular edema,9
E094,1,E0941,Drug/chem diabetes w neuro comp w diabetic mononeuropathy,Drug or chemical induced diabetes mellitus with neurological complications with diabetic mononeuropathy,Drug or chemical induced diabetes mellitus with neurological complications,9
E095,1,E0951,Drug/chem diabetes w diabetic prph angiopath w/o gangrene,Drug or chemical induced diabetes mellitus with diabetic peripheral angiopathy without gangrene,Drug or chemical induced diabetes mellitus with circulatory complications,9
E0962,1,E09621,Drug or chemical induced diabetes mellitus with foot ulcer,Drug or chemical induced diabetes mellitus with foot ulcer,Drug or chemical induced diabetes mellitus with skin complications,9
E0964,1,E09641,Drug/chem diabetes mellitus w hypoglycemia w coma,Drug or chemical induced diabetes mellitus with hypoglycemia with coma,Drug or chemical induced diabetes mellitus with hypoglycemia,9
E101,1,E1011,Type 1 diabetes mellitus with ketoacidosis with coma,Type 1 diabetes mellitus with ketoacidosis with coma,Type 1 diabetes mellitus with ketoacidosis,9
E102,1,E1021,Type 1 diabetes mellitus with diabetic nephropathy,Type 1 diabetes mellitus with diabetic nephropathy,Type 1 diabetes mellitus with kidney complications,9
E1031,1,E10311,Type 1 diabetes w unsp diabetic retinopathy w macular edema,Type 1 diabetes mellitus with unspecified diabetic retinopathy with macular edema,Type 1 diabetes mellitus with unspecified diabetic retinopathy,9
E10321,1,E103211,"Type 1 diab with mild nonp rtnop with macular edema, r eye","Type 1 diabetes mellitus with mild nonproliferative diabetic retinopathy with macular edema, right eye",Type 1 diabetes mellitus with mild nonproliferative diabetic retinopathy with macular edema,9
E10329,1,E103291,"Type 1 diab with mild nonp rtnop without mclr edema, r eye","Type 1 diabetes mellitus with mild nonproliferative diabetic retinopathy without macular edema, right eye",Type 1 diabetes mellitus with mild nonproliferative diabetic retinopathy without macular edema,9
E10331,1,E103311,"Type 1 diab with mod nonp rtnop with macular edema, r eye","Type 1 diabetes mellitus with moderate nonproliferative diabetic retinopathy with macular edema, right eye",Type 1 diabetes mellitus with moderate nonproliferative diabetic retinopathy with macular edema,9
E10339,1,E103391,"Type 1 diab with mod nonp rtnop without macular edema, r eye","Type 1 diabetes mellitus with moderate nonproliferative diabetic retinopathy without macular edema, right eye",Type 1 diabetes mellitus with moderate nonproliferative diabetic retinopathy without macular edema,9
E10341,1,E103411,"Type 1 diab with severe nonp rtnop with macular edema, r eye","Type 1 diabetes mellitus with severe nonproliferative diabetic retinopathy with macular edema, right eye",Type 1 diabetes mellitus with severe nonproliferative diabetic retinopathy with macular edema,9
E10349,1,E103491,"Type 1 diab with severe nonp rtnop without mclr edema, r eye","Type 1 diabetes mellitus with severe nonproliferative diabetic retinopathy without macular edema, right eye",Type 1 diabetes mellitus with severe nonproliferative diabetic retinopathy without macular edema,9
E10351,1,E103511,"Type 1 diab with prolif diab rtnop with macular edema, r eye","Type 1 diabetes mellitus with proliferative diabetic retinopathy with macular edema, right eye",Type 1 diabetes mellitus with proliferative diabetic retinopathy with macular edema,9
E10352,1,E103521,"Type 1 diab w prolif diab rtnop w trctn dtch macula, r eye","Type 1 diabetes mellitus with proliferative diabetic retinopathy with traction retinal detachment involving the macula, right eye",Type 1 diabetes mellitus with proliferative diabetic retinopathy with traction retinal detachment involving the macula,9
E10353,1,E103531,"Type 1 diab w prolif diab rtnop w trctn dtch n-mcla, r eye","Type 1 diabetes mellitus with proliferative diabetic retinopathy with traction retinal detachment not involving the macula, right eye",Type 1 diabetes mellitus with proliferative diabetic retinopathy with traction retinal detachment not involving the macula,9
E10354,1,E103541,"Type 1 diab with prolif diab rtnop with comb detach, r eye","Type 1 diabetes mellitus with proliferative diabetic retinopathy with combined traction retinal detachment and rhegmatogenous retinal detachment, right eye",Type 1 diabetes mellitus with proliferative diabetic retinopathy with combined traction retinal detachment and rhegmatogenous retinal detachment,9
E10355,1,E103551,"Type 1 diabetes with stable prolif diabetic rtnop, right eye","Type 1 diabetes mellitus with stable proliferative diabetic retinopathy, right eye",Type 1 diabetes mellitus with stable proliferative diabetic retinopathy,9
E10359,1,E103591,"Type 1 diab with prolif diab rtnop without mclr edema, r eye","Type 1 diabetes mellitus with proliferative diabetic retinopathy without macular edema, right eye",Type 1 diabetes mellitus with proliferative diabetic retinopathy without macular edema,9
E104,1,E1041,Type 1 diabetes mellitus with diabetic mononeuropathy,Type 1 diabetes mellitus with diabetic mononeuropathy,Type 1 diabetes mellitus with neurological complications,9
E105,1,E1051,Type 1 diabetes w diabetic peripheral angiopath w/o gangrene,Type 1 diabetes mellitus with diabetic peripheral angiopathy without gangrene,Type 1 diabetes mellitus with circulatory complications,9
E1064,1,E10641,Type 1 diabetes mellitus with hypoglycemia with coma,Type 1 diabetes mellitus with hypoglycemia with coma,Type 1 diabetes mellitus with hypoglycemia,9
E110,1,E1101,Type 2 diabetes mellitus with hyperosmolarity with coma,Type 2 diabetes mellitus with hyperosmolarity with coma,Type 2 diabetes mellitus with hyperosmolarity,9
E111,1,E1111,Type 2 diabetes mellitus with ketoacidosis with coma,Type 2 diabetes mellitus with ketoacidosis with coma,Type 2 diabetes mellitus with ketoacidosis,9
E112,1,E1121,Type 2 diabetes mellitus with diabetic nephropathy,Type 2 diabetes mellitus with diabetic nephropathy,Type 2 diabetes mellitus with kidney complications,9
E1131,1,E11311,Type 2 diabetes w unsp diabetic retinopathy w macular edema,Type 2 diabetes mellitus with unspecified diabetic retinopathy with macular edema,Type 2 diabetes mellitus with unspecified diabetic retinopathy,9
E11321,1,E113211,"Type 2 diab with mild nonp rtnop with macular edema, r eye","Type 2 diabetes mellitus with mild nonproliferative diabetic retinopathy with macular edema, right eye",Type 2 diabetes mellitus with mild nonproliferative diabetic retinopathy with macular edema,9
E11329,1,E113291,"Type 2 diab with mild nonp rtnop without mclr edema, r eye","Type 2 diabetes mellitus with mild nonproliferative diabetic retinopathy without macular edema, right eye",Type 2 diabetes mellitus with mild nonproliferative diabetic retinopathy without macular edema,9
E11331,1,E113311,"Type 2 diab with mod nonp rtnop with macular edema, r eye","Type 2 diabetes mellitus with moderate nonproliferative diabetic retinopathy with macular edema, right eye",Type 2 diabetes mellitus with moderate nonproliferative diabetic retinopathy with macular edema,9
E11339,1,E113391,"Type 2 diab with mod nonp rtnop without macular edema, r eye","Type 2 diabetes mellitus with moderate nonproliferative diabetic retinopathy without macular edema, right eye",Type 2 diabetes mellitus with moderate nonproliferative diabetic retinopathy without macular edema,9
E11341,1,E113411,"Type 2 diab with severe nonp rtnop with macular edema, r eye","Type 2 diabetes mellitus with severe nonproliferative diabetic retinopathy with macular edema, right eye",Type 2 diabetes mellitus with severe nonproliferative diabetic retinopathy with macular edema,9
E11349,1,E113491,"Type 2 diab with severe nonp rtnop without mclr edema, r eye","Type 2 diabetes mellitus with severe nonproliferative diabetic retinopathy without macular edema, right eye",Type 2 diabetes mellitus with severe nonproliferative diabetic retinopathy without macular edema,9
E11351,1,E113511,"Type 2 diab with prolif diab rtnop with macular edema, r eye","Type 2 diabetes mellitus with proliferative diabetic retinopathy with macular edema, right eye",Type 2 diabetes mellitus with proliferative diabetic retinopathy with macular edema,9
E11352,1,E113521,"Type 2 diab w prolif diab rtnop w trctn dtch macula, r eye","Type 2 diabetes mellitus with proliferative diabetic retinopathy with traction retinal detachment involving the macula, right eye",Type 2 diabetes mellitus with proliferative diabetic retinopathy with traction retinal detachment involving the macula,9
E11353,1,E113531,"Type 2 diab w prolif diab rtnop w trctn dtch n-mcla, r eye","Type 2 diabetes mellitus with proliferative diabetic retinopathy with traction retinal detachment not involving the macula, right eye",Type 2 diabetes mellitus with proliferative diabetic retinopathy with traction retinal detachment not involving the macula,9
E11354,1,E113541,"Type 2 diab with prolif diab rtnop with comb detach, r eye","Type 2 diabetes mellitus with proliferative diabetic retinopathy with combined traction retinal detachment and rhegmatogenous retinal detachment, right eye",Type 2 diabetes mellitus with proliferative diabetic retinopathy with combined traction retinal detachment and rhegmatogenous retinal detachment,9
E11355,1,E113551,"Type 2 diabetes with stable prolif diabetic rtnop, right eye","Type 2 diabetes mellitus with stable proliferative diabetic retinopathy, right eye",Type 2 diabetes mellitus with stable proliferative diabetic retinopathy,9
E11359,1,E113591,"Type 2 diab with prolif diab rtnop without mclr edema, r eye","Type 2 diabetes mellitus with proliferative diabetic retinopathy without macular edema, right eye",Type 2 diabetes mellitus with proliferative diabetic retinopathy without macular edema,9
E114,1,E1141,Type 2 diabetes mellitus with diabetic mononeuropathy,Type 2 diabetes mellitus with diabetic mononeuropathy,Type 2 diabetes mellitus with neurological complications,9
E115,1,E1151,Type 2 diabetes w diabetic peripheral angiopath w/o gangrene,Type 2 diabetes mellitus with diabetic peripheral angiopathy without gangrene,Type 2 diabetes mellitus with circulatory complications,9
E1162,1,E11621,Type 2 diabetes mellitus with foot ulcer,Type 2 diabetes mellitus with foot ulcer,Type 2 diabetes mellitus with skin complications,9
E1164,1,E11641,Type 2 diabetes mellitus with hypoglycemia with coma,Type 2 diabetes mellitus with hypoglycemia with coma,Type 2 diabetes mellitus with hypoglycemia,9
E130,1,E1301,Oth diabetes mellitus with hyperosmolarity with coma,Other specified diabetes mellitus with hyperosmolarity with coma,Other specified diabetes mellitus with hyperosmolarity,9
E131,1,E1311,Oth diabetes mellitus with ketoacidosis with coma,Other specified diabetes mellitus with ketoacidosis with coma,Other specified diabetes mellitus with ketoacidosis,9
E132,1,E1321,Other specified diabetes mellitus with diabetic nephropathy,Other specified diabetes mellitus with diabetic nephropathy,Other specified diabetes mellitus with kidney complications,9
E1331,1,E13311,Oth diabetes w unsp diabetic retinopathy w macular edema,Other specified diabetes mellitus with unspecified diabetic retinopathy with macular edema,Other specified diabetes mellitus with unspecified diabetic retinopathy,9
E13321,1,E133211,"Oth diabetes with mild nonp rtnop with macular edema, r eye","Other specified diabetes mellitus with mild nonproliferative diabetic retinopathy with macular edema, right eye",Other specified diabetes mellitus with mild nonproliferative diabetic retinopathy with macular edema,9
E13329,1,E133291,"Oth diab with mild nonp rtnop without macular edema, r eye","Other specified diabetes mellitus with mild nonproliferative diabetic retinopathy without macular edema, right eye",Other specified diabetes mellitus with mild nonproliferative diabetic retinopathy without macular edema,9
E13331,1,E133311,"Oth diab with moderate nonp rtnop with macular edema, r eye","Other specified diabetes mellitus with moderate nonproliferative diabetic retinopathy with macular edema, right eye",Other specified diabetes mellitus with moderate nonproliferative diabetic retinopathy with macular edema,9
E64,1,E641,Sequelae of vitamin A deficiency,Sequelae of vitamin A deficiency,Sequelae of malnutrition and other nutritional deficiencies,9
B88,2,B882,Other arthropod infestations,Other arthropod infestations,Other infestations,9
E13339,1,E133391,"Oth diab with mod nonp rtnop without macular edema, r eye","Other specified diabetes mellitus with moderate nonproliferative diabetic retinopathy without macular edema, right eye",Other specified diabetes mellitus with moderate nonproliferative diabetic retinopathy without macular edema,9
E13341,1,E133411,"Oth diab with severe nonp rtnop with macular edema, r eye","Other specified diabetes mellitus with severe nonproliferative diabetic retinopathy with macular edema, right eye",Other specified diabetes mellitus with severe nonproliferative diabetic retinopathy with macular edema,9
E13349,1,E133491,"Oth diab with severe nonp rtnop without macular edema, r eye","Other specified diabetes mellitus with severe nonproliferative diabetic retinopathy without macular edema, right eye",Other specified diabetes mellitus with severe nonproliferative diabetic retinopathy without macular edema,9
E13351,1,E133511,"Oth diab with prolif diab rtnop with macular edema, r eye","Other specified diabetes mellitus with proliferative diabetic retinopathy with macular edema, right eye",Other specified diabetes mellitus with proliferative diabetic retinopathy with macular edema,9
E13352,1,E133521,"Oth diab w prolif diab rtnop with trctn dtch macula, r eye","Other specified diabetes mellitus with proliferative diabetic retinopathy with traction retinal detachment involving the macula, right eye",Other specified diabetes mellitus with proliferative diabetic retinopathy with traction retinal detachment involving the macula,9
E13353,1,E133531,"Oth diab w prolif diab rtnop with trctn dtch n-mcla, r eye","Other specified diabetes mellitus with proliferative diabetic retinopathy with traction retinal detachment not involving the macula, right eye",Other specified diabetes mellitus with proliferative diabetic retinopathy with traction retinal detachment not involving the macula,9
E13354,1,E133541,"Oth diab with prolif diabetic rtnop with comb detach, r eye","Other specified diabetes mellitus with proliferative diabetic retinopathy with combined traction retinal detachment and rhegmatogenous retinal detachment, right eye",Other specified diabetes mellitus with proliferative diabetic retinopathy with combined traction retinal detachment and rhegmatogenous retinal detachment,9
E13355,1,E133551,"Oth diabetes with stable prolif diabetic rtnop, right eye","Other specified diabetes mellitus with stable proliferative diabetic retinopathy, right eye",Other specified diabetes mellitus with stable proliferative diabetic retinopathy,9
E13359,1,E133591,"Oth diab with prolif diab rtnop without macular edema, r eye","Other specified diabetes mellitus with proliferative diabetic retinopathy without macular edema, right eye",Other specified diabetes mellitus with proliferative diabetic retinopathy without macular edema,9
E134,1,E1341,Oth diabetes mellitus with diabetic mononeuropathy,Other specified diabetes mellitus with diabetic mononeuropathy,Other specified diabetes mellitus with neurological complications,9
E135,1,E1351,Oth diabetes w diabetic peripheral angiopathy w/o gangrene,Other specified diabetes mellitus with diabetic peripheral angiopathy without gangrene,Other specified diabetes mellitus with circulatory complications,9
E1362,1,E13621,Other specified diabetes mellitus with foot ulcer,Other specified diabetes mellitus with foot ulcer,Other specified diabetes mellitus with skin complications,9
E1364,1,E13641,Oth diabetes mellitus with hypoglycemia with coma,Other specified diabetes mellitus with hypoglycemia with coma,Other specified diabetes mellitus with hypoglycemia,9
E16,1,E161,Other hypoglycemia,Other hypoglycemia,Other disorders of pancreatic internal secretion,9
E20,1,E201,Pseudohypoparathyroidism,Pseudohypoparathyroidism,Hypoparathyroidism,9
E21,1,E211,"Secondary hyperparathyroidism, not elsewhere classified","Secondary hyperparathyroidism, not elsewhere classified",Hyperparathyroidism and other disorders of parathyroid gland,9
E22,1,E221,Hyperprolactinemia,Hyperprolactinemia,Hyperfunction of pituitary gland,9
E23,1,E231,Drug-induced hypopituitarism,Drug-induced hypopituitarism,Hypofunction and other disorders of the pituitary gland,9
E24,1,E241,Nelson's syndrome,Nelson's syndrome,Cushing's syndrome,9
E260,1,E2601,Conn's syndrome,Conn's syndrome,Primary hyperaldosteronism,9
E268,1,E2681,Bartter's syndrome,Bartter's syndrome,Other hyperaldosteronism,9
E27,1,E271,Primary adrenocortical insufficiency,Primary adrenocortical insufficiency,Other disorders of adrenal gland,9
E28,1,E281,Androgen excess,Androgen excess,Ovarian dysfunction,9
E29,1,E291,Testicular hypofunction,Testicular hypofunction,Testicular dysfunction,9
E30,1,E301,Precocious puberty,Precocious puberty,"Disorders of puberty, not elsewhere classified",9
E31,1,E311,Polyglandular hyperfunction,Polyglandular hyperfunction,Polyglandular dysfunction,9
E312,1,E3121,Multiple endocrine neoplasia [MEN] type I,Multiple endocrine neoplasia [MEN] type I,Multiple endocrine neoplasia [MEN] syndromes,9
E32,1,E321,Abscess of thymus,Abscess of thymus,Diseases of thymus,9
E34,1,E341,Other hypersecretion of intestinal hormones,Other hypersecretion of intestinal hormones,Other endocrine disorders,9
E345,1,E3451,Complete androgen insensitivity syndrome,Complete androgen insensitivity syndrome,Androgen insensitivity syndrome,9
E360,1,E3601,Intraop hemor/hemtom of endo sys org comp an endo sys proc,Intraoperative hemorrhage and hematoma of an endocrine system organ or structure complicating an endocrine system procedure,Intraoperative hemorrhage and hematoma of an endocrine system organ or structure complicating a procedure,9
E361,1,E3611,Acc pnctr & lac of an endo sys org during an endo sys proc,Accidental puncture and laceration of an endocrine system organ or structure during an endocrine system procedure,Accidental puncture and laceration of an endocrine system organ or structure during a procedure,9
E44,1,E441,Mild protein-calorie malnutrition,Mild protein-calorie malnutrition,Protein-calorie malnutrition of moderate and mild degree,9
E50,1,E501,Vitamin A deficiency w Bitot's spot and conjunctival xerosis,Vitamin A deficiency with Bitot's spot and conjunctival xerosis,Vitamin A deficiency,9
E511,1,E5111,Dry beriberi,Dry beriberi,Beriberi,9
E53,1,E531,Pyridoxine deficiency,Pyridoxine deficiency,Deficiency of other B group vitamins,9
E56,1,E561,Deficiency of vitamin K,Deficiency of vitamin K,Other vitamin deficiencies,9
E61,1,E611,Iron deficiency,Iron deficiency,Deficiency of other nutrient elements,9
E63,1,E631,Imbalance of constituents of food intake,Imbalance of constituents of food intake,Other nutritional deficiencies,9
E660,1,E6601,Morbid (severe) obesity due to excess calories,Morbid (severe) obesity due to excess calories,Obesity due to excess calories,9
E67,1,E671,Hypercarotinemia,Hypercarotinemia,Other hyperalimentation,9
E70,1,E701,Other hyperphenylalaninemias,Other hyperphenylalaninemias,Disorders of aromatic amino-acid metabolism,9
E702,1,E7021,Tyrosinemia,Tyrosinemia,Disorders of tyrosine metabolism,9
E7031,1,E70311,Autosomal recessive ocular albinism,Autosomal recessive ocular albinism,Ocular albinism,9
E7032,1,E70321,Tyrosinase positive oculocutaneous albinism,Tyrosinase positive oculocutaneous albinism,Oculocutaneous albinism,9
E7033,1,E70331,Hermansky-Pudlak syndrome,Hermansky-Pudlak syndrome,Albinism with hematologic abnormality,9
E704,1,E7041,Histidinemia,Histidinemia,Disorders of histidine metabolism,9
E7111,1,E71111,3-methylglutaconic aciduria,3-methylglutaconic aciduria,Branched-chain organic acidurias,9
E7112,1,E71121,Propionic acidemia,Propionic acidemia,Disorders of propionate metabolism,9
E7131,1,E71311,Medium chain acyl CoA dehydrogenase deficiency,Medium chain acyl CoA dehydrogenase deficiency,Disorders of fatty-acid oxidation,9
E714,1,E7141,Primary carnitine deficiency,Primary carnitine deficiency,Disorders of carnitine metabolism,9
E7151,1,E71511,Neonatal adrenoleukodystrophy,Neonatal adrenoleukodystrophy,Disorders of peroxisome biogenesis,9
E7152,1,E71521,Adolescent X-linked adrenoleukodystrophy,Adolescent X-linked adrenoleukodystrophy,X-linked adrenoleukodystrophy,9
E7154,1,E71541,Zellweger-like syndrome,Zellweger-like syndrome,Other peroxisomal disorders,9
E720,1,E7201,Cystinuria,Cystinuria,Disorders of amino-acid transport,9
E721,1,E7211,Homocystinuria,Homocystinuria,Disorders of sulfur-bearing amino-acid metabolism,9
E722,1,E7221,Argininemia,Argininemia,Disorders of urea cycle metabolism,9
E725,1,E7251,Non-ketotic hyperglycinemia,Non-ketotic hyperglycinemia,Disorders of glycine metabolism,9
E73,1,E731,Secondary lactase deficiency,Secondary lactase deficiency,Lactose intolerance,9
E740,1,E7401,von Gierke disease,von Gierke disease,Glycogen storage disease,9
E741,1,E7411,Essential fructosuria,Essential fructosuria,Disorders of fructose metabolism,9
E742,1,E7421,Galactosemia,Galactosemia,Disorders of galactose metabolism,9
E743,1,E7431,Sucrase-isomaltase deficiency,Sucrase-isomaltase deficiency,Other disorders of intestinal carbohydrate absorption,9
E750,1,E7501,Sandhoff disease,Sandhoff disease,GM2 gangliosidosis,9
E751,1,E7511,Mucolipidosis IV,Mucolipidosis IV,Other and unspecified gangliosidosis,9
E752,1,E7521,Fabry (-Anderson) disease,Fabry (-Anderson) disease,Other sphingolipidosis,9
E7524,1,E75241,Niemann-Pick disease type B,Niemann-Pick disease type B,Niemann-Pick disease,9
E760,1,E7601,Hurler's syndrome,Hurler's syndrome,"Mucopolysaccharidosis, type I",9
E7621,1,E76211,Morquio B mucopolysaccharidoses,Morquio B mucopolysaccharidoses,Morquio mucopolysaccharidoses,9
E77,1,E771,Defects in glycoprotein degradation,Defects in glycoprotein degradation,Disorders of glycoprotein metabolism,9
E780,1,E7801,Familial hypercholesterolemia,Familial hypercholesterolemia,Pure hypercholesterolemia,9
E787,1,E7871,Barth syndrome,Barth syndrome,Disorders of bile acid and cholesterol metabolism,9
E788,1,E7881,Lipoid dermatoarthritis,Lipoid dermatoarthritis,Other disorders of lipoprotein metabolism,9
E79,1,E791,Lesch-Nyhan syndrome,Lesch-Nyhan syndrome,Disorders of purine and pyrimidine metabolism,9
E80,1,E801,Porphyria cutanea tarda,Porphyria cutanea tarda,Disorders of porphyrin and bilirubin metabolism,9
E802,1,E8021,Acute intermittent (hepatic) porphyria,Acute intermittent (hepatic) porphyria,Other and unspecified porphyria,9
E830,1,E8301,Wilson's disease,Wilson's disease,Disorders of copper metabolism,9
E8311,1,E83111,Hemochromatosis due to repeated red blood cell transfusions,Hemochromatosis due to repeated red blood cell transfusions,Hemochromatosis,9
E833,1,E8331,Familial hypophosphatemia,Familial hypophosphatemia,Disorders of phosphorus metabolism and phosphatases,9
E834,1,E8341,Hypermagnesemia,Hypermagnesemia,Disorders of magnesium metabolism,9
E835,1,E8351,Hypocalcemia,Hypocalcemia,Disorders of calcium metabolism,9
E838,1,E8381,Hungry bone syndrome,Hungry bone syndrome,Other disorders of mineral metabolism,9
E841,1,E8411,Meconium ileus in cystic fibrosis,Meconium ileus in cystic fibrosis,Cystic fibrosis with intestinal manifestations,9
E85,1,E851,Neuropathic heredofamilial amyloidosis,Neuropathic heredofamilial amyloidosis,Amyloidosis,9
E858,1,E8581,Light chain (AL) amyloidosis,Light chain (AL) amyloidosis,Other amyloidosis,9
E86,1,E861,Hypovolemia,Hypovolemia,Volume depletion,9
E87,1,E871,Hypo-osmolality and hyponatremia,Hypo-osmolality and hyponatremia,"Other disorders of fluid, electrolyte and acid-base balance",9
E877,1,E8771,Transfusion associated circulatory overload,Transfusion associated circulatory overload,Fluid overload,9
E880,1,E8801,Alpha-1-antitrypsin deficiency,Alpha-1-antitrypsin deficiency,"Disorders of plasma-protein metabolism, not elsewhere classified",9
E884,1,E8841,MELAS syndrome,MELAS syndrome,Mitochondrial metabolism disorders,9
E888,1,E8881,Metabolic syndrome,Metabolic syndrome,Other specified metabolic disorders,9
E89,1,E891,Postprocedural hypoinsulinemia,Postprocedural hypoinsulinemia,"Postprocedural endocrine and metabolic complications and disorders, not elsewhere classified",9
E894,1,E8941,Symptomatic postprocedural ovarian failure,Symptomatic postprocedural ovarian failure,Postprocedural ovarian failure,9
E8981,1,E89811,Postproc hemor of an endo sys org following other procedure,Postprocedural hemorrhage of an endocrine system organ or structure following other procedure,Postprocedural hemorrhage of an endocrine system organ or structure following a procedure,9
E8982,1,E89821,Postproc hematoma of an endo sys org fol other procedure,Postprocedural hematoma of an endocrine system organ or structure following other procedure,Postprocedural hematoma and seroma of an endocrine system organ or structure,9
F015,1,F0151,Vascular dementia with behavioral disturbance,Vascular dementia with behavioral disturbance,Vascular dementia,9
F028,1,F0281,Dementia in oth diseases classd elswhr w behavioral disturb,Dementia in other diseases classified elsewhere with behavioral disturbance,Dementia in other diseases classified elsewhere,9
F039,1,F0391,Unspecified dementia with behavioral disturbance,Unspecified dementia with behavioral disturbance,Unspecified dementia,9
F06,1,F061,Catatonic disorder due to known physiological condition,Catatonic disorder due to known physiological condition,Other mental disorders due to known physiological condition,9
F063,1,F0631,Mood disorder due to known physiol cond w depressv features,Mood disorder due to known physiological condition with depressive features,Mood disorder due to known physiological condition,9
F078,1,F0781,Postconcussional syndrome,Postconcussional syndrome,Other personality and behavioral disorders due to known physiological condition,9
F101,1,F1011,"Alcohol abuse, in remission","Alcohol abuse, in remission",Alcohol abuse,9
F1012,1,F10121,Alcohol abuse with intoxication delirium,Alcohol abuse with intoxication delirium,Alcohol abuse with intoxication,9
F1015,1,F10151,Alcohol abuse w alcoh-induce psychotic disorder w hallucin,Alcohol abuse with alcohol-induced psychotic disorder with hallucinations,Alcohol abuse with alcohol-induced psychotic disorder,9
F1018,1,F10181,Alcohol abuse with alcohol-induced sexual dysfunction,Alcohol abuse with alcohol-induced sexual dysfunction,Alcohol abuse with other alcohol-induced disorders,9
F102,1,F1021,"Alcohol dependence, in remission","Alcohol dependence, in remission",Alcohol dependence,9
F1022,1,F10221,Alcohol dependence with intoxication delirium,Alcohol dependence with intoxication delirium,Alcohol dependence with intoxication,9
F1023,1,F10231,Alcohol dependence with withdrawal delirium,Alcohol dependence with withdrawal delirium,Alcohol dependence with withdrawal,9
F1025,1,F10251,Alcohol depend w alcoh-induce psychotic disorder w hallucin,Alcohol dependence with alcohol-induced psychotic disorder with hallucinations,Alcohol dependence with alcohol-induced psychotic disorder,9
F1028,1,F10281,Alcohol dependence with alcohol-induced sexual dysfunction,Alcohol dependence with alcohol-induced sexual dysfunction,Alcohol dependence with other alcohol-induced disorders,9
F1092,1,F10921,"Alcohol use, unspecified with intoxication delirium","Alcohol use, unspecified with intoxication delirium","Alcohol use, unspecified with intoxication",9
F1095,1,F10951,"Alcohol use, unsp w alcoh-induce psych disorder w hallucin","Alcohol use, unspecified with alcohol-induced psychotic disorder with hallucinations","Alcohol use, unspecified with alcohol-induced psychotic disorder",9
F1098,1,F10981,"Alcohol use, unsp with alcohol-induced sexual dysfunction","Alcohol use, unspecified with alcohol-induced sexual dysfunction","Alcohol use, unspecified with other alcohol-induced disorders",9
F111,1,F1111,"Opioid abuse, in remission","Opioid abuse, in remission",Opioid abuse,9
F1112,1,F11121,Opioid abuse with intoxication delirium,Opioid abuse with intoxication delirium,Opioid abuse with intoxication,9
F1115,1,F11151,Opioid abuse w opioid-induced psychotic disorder w hallucin,Opioid abuse with opioid-induced psychotic disorder with hallucinations,Opioid abuse with opioid-induced psychotic disorder,9
F1118,1,F11181,Opioid abuse with opioid-induced sexual dysfunction,Opioid abuse with opioid-induced sexual dysfunction,Opioid abuse with other opioid-induced disorder,9
F112,1,F1121,"Opioid dependence, in remission","Opioid dependence, in remission",Opioid dependence,9
F1122,1,F11221,Opioid dependence with intoxication delirium,Opioid dependence with intoxication delirium,Opioid dependence with intoxication,9
F1125,1,F11251,Opioid depend w opioid-induc psychotic disorder w hallucin,Opioid dependence with opioid-induced psychotic disorder with hallucinations,Opioid dependence with opioid-induced psychotic disorder,9
F1128,1,F11281,Opioid dependence with opioid-induced sexual dysfunction,Opioid dependence with opioid-induced sexual dysfunction,Opioid dependence with other opioid-induced disorder,9
F1192,1,F11921,"Opioid use, unspecified with intoxication delirium","Opioid use, unspecified with intoxication delirium","Opioid use, unspecified with intoxication",9
F1195,1,F11951,"Opioid use, unsp w opioid-induc psych disorder w hallucin","Opioid use, unspecified with opioid-induced psychotic disorder with hallucinations","Opioid use, unspecified with opioid-induced psychotic disorder",9
F1198,1,F11981,"Opioid use, unsp with opioid-induced sexual dysfunction","Opioid use, unspecified with opioid-induced sexual dysfunction","Opioid use, unspecified with other specified opioid-induced disorder",9
F121,1,F1211,"Cannabis abuse, in remission","Cannabis abuse, in remission",Cannabis abuse,9
F1212,1,F12121,Cannabis abuse with intoxication delirium,Cannabis abuse with intoxication delirium,Cannabis abuse with intoxication,9
F1215,1,F12151,Cannabis abuse with psychotic disorder with hallucinations,Cannabis abuse with psychotic disorder with hallucinations,Cannabis abuse with psychotic disorder,9
F122,1,F1221,"Cannabis dependence, in remission","Cannabis dependence, in remission",Cannabis dependence,9
F1222,1,F12221,Cannabis dependence with intoxication delirium,Cannabis dependence with intoxication delirium,Cannabis dependence with intoxication,9
F1225,1,F12251,Cannabis dependence w psychotic disorder with hallucinations,Cannabis dependence with psychotic disorder with hallucinations,Cannabis dependence with psychotic disorder,9
F1292,1,F12921,"Cannabis use, unspecified with intoxication delirium","Cannabis use, unspecified with intoxication delirium","Cannabis use, unspecified with intoxication",9
F1295,1,F12951,"Cannabis use, unsp w psychotic disorder with hallucinations","Cannabis use, unspecified with psychotic disorder with hallucinations","Cannabis use, unspecified with psychotic disorder",9
F131,1,F1311,"Sedative, hypnotic or anxiolytic abuse, in remission","Sedative, hypnotic or anxiolytic abuse, in remission","Sedative, hypnotic or anxiolytic-related abuse",9
F1312,1,F13121,Sedatv/hyp/anxiolytc abuse w intoxication delirium,"Sedative, hypnotic or anxiolytic abuse with intoxication delirium","Sedative, hypnotic or anxiolytic abuse with intoxication",9
F1315,1,F13151,Sedatv/hyp/anxiolytc abuse w psychotic disorder w hallucin,"Sedative, hypnotic or anxiolytic abuse with sedative, hypnotic or anxiolytic-induced psychotic disorder with hallucinations","Sedative, hypnotic or anxiolytic abuse with sedative, hypnotic or anxiolytic-induced psychotic disorder",9
F1318,1,F13181,"Sedative, hypnotic or anxiolytic abuse w sexual dysfunction","Sedative, hypnotic or anxiolytic abuse with sedative, hypnotic or anxiolytic-induced sexual dysfunction","Sedative, hypnotic or anxiolytic abuse with other sedative, hypnotic or anxiolytic-induced disorders",9
F132,1,F1321,"Sedative, hypnotic or anxiolytic dependence, in remission","Sedative, hypnotic or anxiolytic dependence, in remission","Sedative, hypnotic or anxiolytic-related dependence",9
F1322,1,F13221,Sedatv/hyp/anxiolytc dependence w intoxication delirium,"Sedative, hypnotic or anxiolytic dependence with intoxication delirium","Sedative, hypnotic or anxiolytic dependence with intoxication",9
F1323,1,F13231,Sedatv/hyp/anxiolytc dependence w withdrawal delirium,"Sedative, hypnotic or anxiolytic dependence with withdrawal delirium","Sedative, hypnotic or anxiolytic dependence with withdrawal",9
F1325,1,F13251,Sedatv/hyp/anxiolytc depend w psychotic disorder w hallucin,"Sedative, hypnotic or anxiolytic dependence with sedative, hypnotic or anxiolytic-induced psychotic disorder with hallucinations","Sedative, hypnotic or anxiolytic dependence with sedative, hypnotic or anxiolytic-induced psychotic disorder",9
F1328,1,F13281,Sedatv/hyp/anxiolytc dependence w sexual dysfunction,"Sedative, hypnotic or anxiolytic dependence with sedative, hypnotic or anxiolytic-induced sexual dysfunction","Sedative, hypnotic or anxiolytic dependence with other sedative, hypnotic or anxiolytic-induced disorders",9
F1392,1,F13921,"Sedatv/hyp/anxiolytc use, unsp w intoxication delirium","Sedative, hypnotic or anxiolytic use, unspecified with intoxication delirium","Sedative, hypnotic or anxiolytic use, unspecified with intoxication",9
F1393,1,F13931,"Sedatv/hyp/anxiolytc use, unsp w withdrawal delirium","Sedative, hypnotic or anxiolytic use, unspecified with withdrawal delirium","Sedative, hypnotic or anxiolytic use, unspecified with withdrawal",9
F1395,1,F13951,"Sedatv/hyp/anxiolytc use, unsp w psych disorder w hallucin","Sedative, hypnotic or anxiolytic use, unspecified with sedative, hypnotic or anxiolytic-induced psychotic disorder with hallucinations","Sedative, hypnotic or anxiolytic use, unspecified with sedative, hypnotic or anxiolytic-induced psychotic disorder",9
F1398,1,F13981,"Sedatv/hyp/anxiolytc use, unsp w sexual dysfunction","Sedative, hypnotic or anxiolytic use, unspecified with sedative, hypnotic or anxiolytic-induced sexual dysfunction","Sedative, hypnotic or anxiolytic use, unspecified with other sedative, hypnotic or anxiolytic-induced disorders",9
F141,1,F1411,"Cocaine abuse, in remission","Cocaine abuse, in remission",Cocaine abuse,9
F1412,1,F14121,Cocaine abuse with intoxication with delirium,Cocaine abuse with intoxication with delirium,Cocaine abuse with intoxication,9
F1415,1,F14151,Cocaine abuse w cocaine-induc psychotic disorder w hallucin,Cocaine abuse with cocaine-induced psychotic disorder with hallucinations,Cocaine abuse with cocaine-induced psychotic disorder,9
F1418,1,F14181,Cocaine abuse with cocaine-induced sexual dysfunction,Cocaine abuse with cocaine-induced sexual dysfunction,Cocaine abuse with other cocaine-induced disorder,9
F142,1,F1421,"Cocaine dependence, in remission","Cocaine dependence, in remission",Cocaine dependence,9
F1422,1,F14221,Cocaine dependence with intoxication delirium,Cocaine dependence with intoxication delirium,Cocaine dependence with intoxication,9
F1425,1,F14251,Cocaine depend w cocaine-induc psychotic disorder w hallucin,Cocaine dependence with cocaine-induced psychotic disorder with hallucinations,Cocaine dependence with cocaine-induced psychotic disorder,9
F1428,1,F14281,Cocaine dependence with cocaine-induced sexual dysfunction,Cocaine dependence with cocaine-induced sexual dysfunction,Cocaine dependence with other cocaine-induced disorder,9
F1492,1,F14921,"Cocaine use, unspecified with intoxication delirium","Cocaine use, unspecified with intoxication delirium","Cocaine use, unspecified with intoxication",9
F1495,1,F14951,"Cocaine use, unsp w cocaine-induc psych disorder w hallucin","Cocaine use, unspecified with cocaine-induced psychotic disorder with hallucinations","Cocaine use, unspecified with cocaine-induced psychotic disorder",9
F1498,1,F14981,"Cocaine use, unsp with cocaine-induced sexual dysfunction","Cocaine use, unspecified with cocaine-induced sexual dysfunction","Cocaine use, unspecified with other specified cocaine-induced disorder",9
F151,1,F1511,"Other stimulant abuse, in remission","Other stimulant abuse, in remission",Other stimulant abuse,9
F1512,1,F15121,Other stimulant abuse with intoxication delirium,Other stimulant abuse with intoxication delirium,Other stimulant abuse with intoxication,9
F1515,1,F15151,Oth stimulant abuse w stim-induce psych disorder w hallucin,Other stimulant abuse with stimulant-induced psychotic disorder with hallucinations,Other stimulant abuse with stimulant-induced psychotic disorder,9
F1518,1,F15181,Oth stimulant abuse w stimulant-induced sexual dysfunction,Other stimulant abuse with stimulant-induced sexual dysfunction,Other stimulant abuse with other stimulant-induced disorder,9
F152,1,F1521,"Other stimulant dependence, in remission","Other stimulant dependence, in remission",Other stimulant dependence,9
F1522,1,F15221,Other stimulant dependence with intoxication delirium,Other stimulant dependence with intoxication delirium,Other stimulant dependence with intoxication,9
F1525,1,F15251,Oth stimulant depend w stim-induce psych disorder w hallucin,Other stimulant dependence with stimulant-induced psychotic disorder with hallucinations,Other stimulant dependence with stimulant-induced psychotic disorder,9
F1528,1,F15281,Oth stimulant dependence w stim-induce sexual dysfunction,Other stimulant dependence with stimulant-induced sexual dysfunction,Other stimulant dependence with other stimulant-induced disorder,9
F1592,1,F15921,"Other stimulant use, unspecified with intoxication delirium","Other stimulant use, unspecified with intoxication delirium","Other stimulant use, unspecified with intoxication",9
F1595,1,F15951,"Oth stim use, unsp w stim-induce psych disorder w hallucin","Other stimulant use, unspecified with stimulant-induced psychotic disorder with hallucinations","Other stimulant use, unspecified with stimulant-induced psychotic disorder",9
F1598,1,F15981,"Oth stimulant use, unsp w stim-induce sexual dysfunction","Other stimulant use, unspecified with stimulant-induced sexual dysfunction","Other stimulant use, unspecified with other stimulant-induced disorder",9
F161,1,F1611,"Hallucinogen abuse, in remission","Hallucinogen abuse, in remission",Hallucinogen abuse,9
F1612,1,F16121,Hallucinogen abuse with intoxication with delirium,Hallucinogen abuse with intoxication with delirium,Hallucinogen abuse with intoxication,9
B268,3,B2683,Mumps nephritis,Mumps nephritis,Mumps with other complications,9
F1615,1,F16151,Hallucinogen abuse w psychotic disorder w hallucinations,Hallucinogen abuse with hallucinogen-induced psychotic disorder with hallucinations,Hallucinogen abuse with hallucinogen-induced psychotic disorder,9
F162,1,F1621,"Hallucinogen dependence, in remission","Hallucinogen dependence, in remission",Hallucinogen dependence,9
F1622,1,F16221,Hallucinogen dependence with intoxication with delirium,Hallucinogen dependence with intoxication with delirium,Hallucinogen dependence with intoxication,9
F1625,1,F16251,Hallucinogen dependence w psychotic disorder w hallucin,Hallucinogen dependence with hallucinogen-induced psychotic disorder with hallucinations,Hallucinogen dependence with hallucinogen-induced psychotic disorder,9
F1692,1,F16921,"Hallucinogen use, unsp with intoxication with delirium","Hallucinogen use, unspecified with intoxication with delirium","Hallucinogen use, unspecified with intoxication",9
F1695,1,F16951,"Hallucinogen use, unsp w psychotic disorder w hallucinations","Hallucinogen use, unspecified with hallucinogen-induced psychotic disorder with hallucinations","Hallucinogen use, unspecified with hallucinogen-induced psychotic disorder",9
F1720,1,F17201,"Nicotine dependence, unspecified, in remission","Nicotine dependence, unspecified, in remission","Nicotine dependence, unspecified",9
F1721,1,F17211,"Nicotine dependence, cigarettes, in remission","Nicotine dependence, cigarettes, in remission","Nicotine dependence, cigarettes",9
F1722,1,F17221,"Nicotine dependence, chewing tobacco, in remission","Nicotine dependence, chewing tobacco, in remission","Nicotine dependence, chewing tobacco",9
F1729,1,F17291,"Nicotine dependence, other tobacco product, in remission","Nicotine dependence, other tobacco product, in remission","Nicotine dependence, other tobacco product",9
F181,1,F1811,"Inhalant abuse, in remission","Inhalant abuse, in remission",Inhalant abuse,9
F1812,1,F18121,Inhalant abuse with intoxication delirium,Inhalant abuse with intoxication delirium,Inhalant abuse with intoxication,9
F1815,1,F18151,Inhalant abuse w inhalnt-induce psych disorder w hallucin,Inhalant abuse with inhalant-induced psychotic disorder with hallucinations,Inhalant abuse with inhalant-induced psychotic disorder,9
F182,1,F1821,"Inhalant dependence, in remission","Inhalant dependence, in remission",Inhalant dependence,9
F1822,1,F18221,Inhalant dependence with intoxication delirium,Inhalant dependence with intoxication delirium,Inhalant dependence with intoxication,9
F1825,1,F18251,Inhalant depend w inhalnt-induce psych disorder w hallucin,Inhalant dependence with inhalant-induced psychotic disorder with hallucinations,Inhalant dependence with inhalant-induced psychotic disorder,9
F1892,1,F18921,"Inhalant use, unspecified with intoxication with delirium","Inhalant use, unspecified with intoxication with delirium","Inhalant use, unspecified with intoxication",9
F1895,1,F18951,"Inhalant use, unsp w inhalnt-induce psych disord w hallucin","Inhalant use, unspecified with inhalant-induced psychotic disorder with hallucinations","Inhalant use, unspecified with inhalant-induced psychotic disorder",9
F191,1,F1911,"Other psychoactive substance abuse, in remission","Other psychoactive substance abuse, in remission",Other psychoactive substance abuse,9
F1912,1,F19121,Oth psychoactive substance abuse with intoxication delirium,Other psychoactive substance abuse with intoxication delirium,Other psychoactive substance abuse with intoxication,9
F1915,1,F19151,Oth psychoactv substance abuse w psych disorder w hallucin,Other psychoactive substance abuse with psychoactive substance-induced psychotic disorder with hallucinations,Other psychoactive substance abuse with psychoactive substance-induced psychotic disorder,9
F1918,1,F19181,Oth psychoactive substance abuse w sexual dysfunction,Other psychoactive substance abuse with psychoactive substance-induced sexual dysfunction,Other psychoactive substance abuse with other psychoactive substance-induced disorders,9
F192,1,F1921,"Other psychoactive substance dependence, in remission","Other psychoactive substance dependence, in remission",Other psychoactive substance dependence,9
F1922,1,F19221,Oth psychoactive substance dependence w intox delirium,Other psychoactive substance dependence with intoxication delirium,Other psychoactive substance dependence with intoxication,9
F1923,1,F19231,Oth psychoactive substance dependence w withdrawal delirium,Other psychoactive substance dependence with withdrawal delirium,Other psychoactive substance dependence with withdrawal,9
F1925,1,F19251,Oth psychoactv substance depend w psych disorder w hallucin,Other psychoactive substance dependence with psychoactive substance-induced psychotic disorder with hallucinations,Other psychoactive substance dependence with psychoactive substance-induced psychotic disorder,9
F1928,1,F19281,Oth psychoactive substance dependence w sexual dysfunction,Other psychoactive substance dependence with psychoactive substance-induced sexual dysfunction,Other psychoactive substance dependence with other psychoactive substance-induced disorders,9
F1992,1,F19921,"Oth psychoactive substance use, unsp w intox w delirium","Other psychoactive substance use, unspecified with intoxication with delirium","Other psychoactive substance use, unspecified with intoxication",9
F1993,1,F19931,"Oth psychoactive substance use, unsp w withdrawal delirium","Other psychoactive substance use, unspecified with withdrawal delirium","Other psychoactive substance use, unspecified with withdrawal",9
F1995,1,F19951,"Oth psychoactv sub use, unsp w psych disorder w hallucin","Other psychoactive substance use, unspecified with psychoactive substance-induced psychotic disorder with hallucinations","Other psychoactive substance use, unspecified with psychoactive substance-induced psychotic disorder",9
F1998,1,F19981,"Oth psychoactive substance use, unsp w sexual dysfunction","Other psychoactive substance use, unspecified with psychoactive substance-induced sexual dysfunction","Other psychoactive substance use, unspecified with other psychoactive substance-induced disorders",9
F20,1,F201,Disorganized schizophrenia,Disorganized schizophrenia,Schizophrenia,9
F208,1,F2081,Schizophreniform disorder,Schizophreniform disorder,Other schizophrenia,9
F25,1,F251,"Schizoaffective disorder, depressive type","Schizoaffective disorder, depressive type",Schizoaffective disorders,9
F301,1,F3011,"Manic episode without psychotic symptoms, mild","Manic episode without psychotic symptoms, mild",Manic episode without psychotic symptoms,9
F311,1,F3111,"Bipolar disord, crnt episode manic w/o psych features, mild","Bipolar disorder, current episode manic without psychotic features, mild","Bipolar disorder, current episode manic without psychotic features",9
F313,1,F3131,"Bipolar disorder, current episode depressed, mild","Bipolar disorder, current episode depressed, mild","Bipolar disorder, current episode depressed, mild or moderate severity",9
F316,1,F3161,"Bipolar disorder, current episode mixed, mild","Bipolar disorder, current episode mixed, mild","Bipolar disorder, current episode mixed",9
F317,1,F3171,"Bipolar disord, in partial remis, most recent epsd hypomanic","Bipolar disorder, in partial remission, most recent episode hypomanic","Bipolar disorder, currently in remission",9
F318,1,F3181,Bipolar II disorder,Bipolar II disorder,Other bipolar disorders,9
F32,1,F321,"Major depressive disorder, single episode, moderate","Major depressive disorder, single episode, moderate","Major depressive disorder, single episode",9
F328,1,F3281,Premenstrual dysphoric disorder,Premenstrual dysphoric disorder,Other depressive episodes,9
F33,1,F331,"Major depressive disorder, recurrent, moderate","Major depressive disorder, recurrent, moderate","Major depressive disorder, recurrent",9
F334,1,F3341,"Major depressive disorder, recurrent, in partial remission","Major depressive disorder, recurrent, in partial remission","Major depressive disorder, recurrent, in remission",9
F34,1,F341,Dysthymic disorder,Dysthymic disorder,Persistent mood [affective] disorders,9
F348,1,F3481,Disruptive mood dysregulation disorder,Disruptive mood dysregulation disorder,Other persistent mood [affective] disorders,9
F400,1,F4001,Agoraphobia with panic disorder,Agoraphobia with panic disorder,Agoraphobia,9
F401,1,F4011,"Social phobia, generalized","Social phobia, generalized",Social phobias,9
F4023,1,F40231,Fear of injections and transfusions,Fear of injections and transfusions,"Blood, injection, injury type phobia",9
F4024,1,F40241,Acrophobia,Acrophobia,Situational type phobia,9
F4029,1,F40291,Gynephobia,Gynephobia,Other specified phobia,9
F41,1,F411,Generalized anxiety disorder,Generalized anxiety disorder,Other anxiety disorders,9
F431,1,F4311,"Post-traumatic stress disorder, acute","Post-traumatic stress disorder, acute",Post-traumatic stress disorder (PTSD),9
F432,1,F4321,Adjustment disorder with depressed mood,Adjustment disorder with depressed mood,Adjustment disorders,9
F44,1,F441,Dissociative fugue,Dissociative fugue,Dissociative and conversion disorders,9
F448,1,F4481,Dissociative identity disorder,Dissociative identity disorder,Other dissociative and conversion disorders,9
F45,1,F451,Undifferentiated somatoform disorder,Undifferentiated somatoform disorder,Somatoform disorders,9
F452,1,F4521,Hypochondriasis,Hypochondriasis,Hypochondriacal disorders,9
F454,1,F4541,Pain disorder exclusively related to psychological factors,Pain disorder exclusively related to psychological factors,Pain disorders related to psychological factors,9
F48,1,F481,Depersonalization-derealization syndrome,Depersonalization-derealization syndrome,Other nonpsychotic mental disorders,9
F500,1,F5001,"Anorexia nervosa, restricting type","Anorexia nervosa, restricting type",Anorexia nervosa,9
F508,1,F5081,Binge eating disorder,Binge eating disorder,Other eating disorders,9
F510,1,F5101,Primary insomnia,Primary insomnia,Insomnia not due to a substance or known physiological condition,9
F511,1,F5111,Primary hypersomnia,Primary hypersomnia,Hypersomnia not due to a substance or known physiological condition,9
F52,1,F521,Sexual aversion disorder,Sexual aversion disorder,Sexual dysfunction not due to a substance or known physiological condition,9
F522,1,F5221,Male erectile disorder,Male erectile disorder,Sexual arousal disorders,9
F523,1,F5231,Female orgasmic disorder,Female orgasmic disorder,Orgasmic disorder,9
F55,1,F551,Abuse of herbal or folk remedies,Abuse of herbal or folk remedies,Abuse of non-psychoactive substances,9
F60,1,F601,Schizoid personality disorder,Schizoid personality disorder,Specific personality disorders,9
F608,1,F6081,Narcissistic personality disorder,Narcissistic personality disorder,Other specific personality disorders,9
F63,1,F631,Pyromania,Pyromania,Impulse disorders,9
F638,1,F6381,Intermittent explosive disorder,Intermittent explosive disorder,Other impulse disorders,9
F64,1,F641,Dual role transvestism,Dual role transvestism,Gender identity disorders,9
F65,1,F651,Transvestic fetishism,Transvestic fetishism,Paraphilias,9
F655,1,F6551,Sexual masochism,Sexual masochism,Sadomasochism,9
F658,1,F6581,Frotteurism,Frotteurism,Other paraphilias,9
F681,1,F6811,Factitious disorder w predom psych signs and symptoms,Factitious disorder with predominantly psychological signs and symptoms,Factitious disorder,9
F80,1,F801,Expressive language disorder,Expressive language disorder,Specific developmental disorders of speech and language,9
F808,1,F8081,Childhood onset fluency disorder,Childhood onset fluency disorder,Other developmental disorders of speech and language,9
F818,1,F8181,Disorder of written expression,Disorder of written expression,Other developmental disorders of scholastic skills,9
F90,1,F901,"Attn-defct hyperactivity disorder, predom hyperactive type","Attention-deficit hyperactivity disorder, predominantly hyperactive type",Attention-deficit hyperactivity disorders,9
F91,1,F911,"Conduct disorder, childhood-onset type","Conduct disorder, childhood-onset type",Conduct disorders,9
F94,1,F941,Reactive attachment disorder of childhood,Reactive attachment disorder of childhood,Disorders of social functioning with onset specific to childhood and adolescence,9
F95,1,F951,Chronic motor or vocal tic disorder,Chronic motor or vocal tic disorder,Tic disorder,9
F98,1,F981,Encopresis not due to a substance or known physiol condition,Encopresis not due to a substance or known physiological condition,Other behavioral and emotional disorders with onset usually occurring in childhood and adolescence,9
F982,1,F9821,Rumination disorder of infancy,Rumination disorder of infancy,Other feeding disorders of infancy and childhood,9
G00,1,G001,Pneumococcal meningitis,Pneumococcal meningitis,"Bacterial meningitis, not elsewhere classified",9
G03,1,G031,Chronic meningitis,Chronic meningitis,Meningitis due to other and unspecified causes,9
B48,4,B484,Penicillosis,Penicillosis,"Other mycoses, not elsewhere classified",9
G040,1,G0401,Postinfect acute dissem encephalitis and encephalomyelitis,Postinfectious acute disseminated encephalitis and encephalomyelitis (postinfectious ADEM),Acute disseminated encephalitis and encephalomyelitis (ADEM),9
G043,1,G0431,Postinfectious acute necrotizing hemorrhagic encephalopathy,Postinfectious acute necrotizing hemorrhagic encephalopathy,Acute necrotizing hemorrhagic encephalopathy,9
G048,1,G0481,Other encephalitis and encephalomyelitis,Other encephalitis and encephalomyelitis,"Other encephalitis, myelitis and encephalomyelitis",9
G049,1,G0491,"Myelitis, unspecified","Myelitis, unspecified","Encephalitis, myelitis and encephalomyelitis, unspecified",9
G06,1,G061,Intraspinal abscess and granuloma,Intraspinal abscess and granuloma,Intracranial and intraspinal abscess and granuloma,9
G11,1,G111,Early-onset cerebellar ataxia,Early-onset cerebellar ataxia,Hereditary ataxia,9
G12,1,G121,Other inherited spinal muscular atrophy,Other inherited spinal muscular atrophy,Spinal muscular atrophy and related syndromes,9
G122,1,G1221,Amyotrophic lateral sclerosis,Amyotrophic lateral sclerosis,Motor neuron disease,9
G13,1,G131,Oth systemic atrophy aff cnsl in neoplastic disease,Other systemic atrophy primarily affecting central nervous system in neoplastic disease,Systemic atrophies primarily affecting central nervous system in diseases classified elsewhere,9
G211,1,G2111,Neuroleptic induced parkinsonism,Neuroleptic induced parkinsonism,Other drug-induced secondary parkinsonism,9
G23,1,G231,Progressive supranuclear ophthalmoplegia,Progressive supranuclear ophthalmoplegia [Steele-Richardson-Olszewski],Other degenerative diseases of basal ganglia,9
G240,1,G2401,Drug induced subacute dyskinesia,Drug induced subacute dyskinesia,Drug induced dystonia,9
G25,1,G251,Drug-induced tremor,Drug-induced tremor,Other extrapyramidal and movement disorders,9
G256,1,G2561,Drug induced tics,Drug induced tics,Drug induced tics and other tics of organic origin,9
G257,1,G2571,Drug induced akathisia,Drug induced akathisia,Other and unspecified drug induced movement disorders,9
G258,1,G2581,Restless legs syndrome,Restless legs syndrome,Other specified extrapyramidal and movement disorders,9
G30,1,G301,Alzheimer's disease with late onset,Alzheimer's disease with late onset,Alzheimer's disease,9
G310,1,G3101,Pick's disease,Pick's disease,Frontotemporal dementia,9
G318,1,G3181,Alpers disease,Alpers disease,Other specified degenerative diseases of nervous system,9
G328,1,G3281,Cerebellar ataxia in diseases classified elsewhere,Cerebellar ataxia in diseases classified elsewhere,Other specified degenerative disorders of nervous system in diseases classified elsewhere,9
G36,1,G361,Acute and subacute hemorrhagic leukoencephalitis [Hurst],Acute and subacute hemorrhagic leukoencephalitis [Hurst],Other acute disseminated demyelination,9
G37,1,G371,Central demyelination of corpus callosum,Central demyelination of corpus callosum,Other demyelinating diseases of central nervous system,9
G4000,1,G40001,"Local-rel idio epi w seiz of loc onst, not ntrct, w stat epi","Localization-related (focal) (partial) idiopathic epilepsy and epileptic syndromes with seizures of localized onset, not intractable, with status epilepticus","Localization-related (focal) (partial) idiopathic epilepsy and epileptic syndromes with seizures of localized onset, not intractable",9
G4001,1,G40011,"Local-rel idio epi w seiz of loc onset, ntrct, w stat epi","Localization-related (focal) (partial) idiopathic epilepsy and epileptic syndromes with seizures of localized onset, intractable, with status epilepticus","Localization-related (focal) (partial) idiopathic epilepsy and epileptic syndromes with seizures of localized onset, intractable",9
G4010,1,G40101,"Local-rel symptc epi w simp part seiz, not ntrct, w stat epi","Localization-related (focal) (partial) symptomatic epilepsy and epileptic syndromes with simple partial seizures, not intractable, with status epilepticus","Localization-related (focal) (partial) symptomatic epilepsy and epileptic syndromes with simple partial seizures, not intractable",9
G4011,1,G40111,"Local-rel symptc epi w simple part seiz, ntrct, w stat epi","Localization-related (focal) (partial) symptomatic epilepsy and epileptic syndromes with simple partial seizures, intractable, with status epilepticus","Localization-related (focal) (partial) symptomatic epilepsy and epileptic syndromes with simple partial seizures, intractable",9
G4020,1,G40201,"Local-rel symptc epi w cmplx prt seiz, not ntrct, w stat epi","Localization-related (focal) (partial) symptomatic epilepsy and epileptic syndromes with complex partial seizures, not intractable, with status epilepticus","Localization-related (focal) (partial) symptomatic epilepsy and epileptic syndromes with complex partial seizures, not intractable",9
G4021,1,G40211,"Local-rel symptc epi w cmplx partial seiz, ntrct, w stat epi","Localization-related (focal) (partial) symptomatic epilepsy and epileptic syndromes with complex partial seizures, intractable, with status epilepticus","Localization-related (focal) (partial) symptomatic epilepsy and epileptic syndromes with complex partial seizures, intractable",9
G4030,1,G40301,"Gen idiopathic epilepsy, not intractable, w stat epi","Generalized idiopathic epilepsy and epileptic syndromes, not intractable, with status epilepticus","Generalized idiopathic epilepsy and epileptic syndromes, not intractable",9
G4031,1,G40311,"Generalized idiopathic epilepsy, intractable, w stat epi","Generalized idiopathic epilepsy and epileptic syndromes, intractable, with status epilepticus","Generalized idiopathic epilepsy and epileptic syndromes, intractable",9
G40A0,1,G40A01,"Absence epileptic syndrome, not intractable, w stat epi","Absence epileptic syndrome, not intractable, with status epilepticus","Absence epileptic syndrome, not intractable",9
G40A1,1,G40A11,"Absence epileptic syndrome, intractable, w stat epi","Absence epileptic syndrome, intractable, with status epilepticus","Absence epileptic syndrome, intractable",9
G40B0,1,G40B01,"Juvenile myoclonic epilepsy, not intractable, w stat epi","Juvenile myoclonic epilepsy, not intractable, with status epilepticus","Juvenile myoclonic epilepsy, not intractable",9
G40B1,1,G40B11,"Juvenile myoclonic epilepsy, intractable, w stat epi","Juvenile myoclonic epilepsy, intractable, with status epilepticus","Juvenile myoclonic epilepsy, intractable",9
G4040,1,G40401,"Oth generalized epilepsy, not intractable, w stat epi","Other generalized epilepsy and epileptic syndromes, not intractable, with status epilepticus","Other generalized epilepsy and epileptic syndromes, not intractable",9
G4430,1,G44301,"Post-traumatic headache, unspecified, intractable","Post-traumatic headache, unspecified, intractable","Post-traumatic headache, unspecified",9
G4041,1,G40411,"Oth generalized epilepsy, intractable, w status epilepticus","Other generalized epilepsy and epileptic syndromes, intractable, with status epilepticus","Other generalized epilepsy and epileptic syndromes, intractable",9
G4050,1,G40501,"Epileptic seiz rel to extrn causes, not ntrct, w stat epi","Epileptic seizures related to external causes, not intractable, with status epilepticus","Epileptic seizures related to external causes, not intractable",9
G4080,1,G40801,"Other epilepsy, not intractable, with status epilepticus","Other epilepsy, not intractable, with status epilepticus",Other epilepsy,9
G4081,1,G40811,"Lennox-Gastaut syndrome, not intractable, w stat epi","Lennox-Gastaut syndrome, not intractable, with status epilepticus",Lennox-Gastaut syndrome,9
G4082,1,G40821,"Epileptic spasms, not intractable, with status epilepticus","Epileptic spasms, not intractable, with status epilepticus",Epileptic spasms,9
G4090,1,G40901,"Epilepsy, unsp, not intractable, with status epilepticus","Epilepsy, unspecified, not intractable, with status epilepticus","Epilepsy, unspecified, not intractable",9
G4091,1,G40911,"Epilepsy, unspecified, intractable, with status epilepticus","Epilepsy, unspecified, intractable, with status epilepticus","Epilepsy, unspecified, intractable",9
G4300,1,G43001,"Migraine w/o aura, not intractable, with status migrainosus","Migraine without aura, not intractable, with status migrainosus","Migraine without aura, not intractable",9
G4301,1,G43011,"Migraine without aura, intractable, with status migrainosus","Migraine without aura, intractable, with status migrainosus","Migraine without aura, intractable",9
G4310,1,G43101,"Migraine with aura, not intractable, with status migrainosus","Migraine with aura, not intractable, with status migrainosus","Migraine with aura, not intractable",9
G4311,1,G43111,"Migraine with aura, intractable, with status migrainosus","Migraine with aura, intractable, with status migrainosus","Migraine with aura, intractable",9
G4340,1,G43401,"Hemiplegic migraine, not intractable, w status migrainosus","Hemiplegic migraine, not intractable, with status migrainosus","Hemiplegic migraine, not intractable",9
G4341,1,G43411,"Hemiplegic migraine, intractable, with status migrainosus","Hemiplegic migraine, intractable, with status migrainosus","Hemiplegic migraine, intractable",9
G4350,1,G43501,"Perst migraine aura w/o cereb infrc, not ntrct, w stat migr","Persistent migraine aura without cerebral infarction, not intractable, with status migrainosus","Persistent migraine aura without cerebral infarction, not intractable",9
G4351,1,G43511,"Perst migraine aura w/o cerebral infrc, ntrct, w stat migr","Persistent migraine aura without cerebral infarction, intractable, with status migrainosus","Persistent migraine aura without cerebral infarction, intractable",9
G4360,1,G43601,"Perst migraine aura w cerebral infrc, not ntrct, w stat migr","Persistent migraine aura with cerebral infarction, not intractable, with status migrainosus","Persistent migraine aura with cerebral infarction, not intractable",9
G4361,1,G43611,"Perst migraine aura w cerebral infrc, ntrct, w stat migr","Persistent migraine aura with cerebral infarction, intractable, with status migrainosus","Persistent migraine aura with cerebral infarction, intractable",9
G4370,1,G43701,"Chronic migraine w/o aura, not intractable, w stat migr","Chronic migraine without aura, not intractable, with status migrainosus","Chronic migraine without aura, not intractable",9
G4371,1,G43711,"Chronic migraine w/o aura, intractable, w status migrainosus","Chronic migraine without aura, intractable, with status migrainosus","Chronic migraine without aura, intractable",9
G43A,1,G43A1,"Cyclical vomiting, intractable","Cyclical vomiting, intractable",Cyclical vomiting,9
G43B,1,G43B1,"Ophthalmoplegic migraine, intractable","Ophthalmoplegic migraine, intractable",Ophthalmoplegic migraine,9
G43C,1,G43C1,"Periodic headache syndromes in child or adult, intractable","Periodic headache syndromes in child or adult, intractable",Periodic headache syndromes in child or adult,9
G43D,1,G43D1,"Abdominal migraine, intractable","Abdominal migraine, intractable",Abdominal migraine,9
G4380,1,G43801,"Other migraine, not intractable, with status migrainosus","Other migraine, not intractable, with status migrainosus","Other migraine, not intractable",9
G4381,1,G43811,"Other migraine, intractable, with status migrainosus","Other migraine, intractable, with status migrainosus","Other migraine, intractable",9
G4382,1,G43821,"Menstrual migraine, not intractable, with status migrainosus","Menstrual migraine, not intractable, with status migrainosus","Menstrual migraine, not intractable",9
G4383,1,G43831,"Menstrual migraine, intractable, with status migrainosus","Menstrual migraine, intractable, with status migrainosus","Menstrual migraine, intractable",9
G4390,1,G43901,"Migraine, unsp, not intractable, with status migrainosus","Migraine, unspecified, not intractable, with status migrainosus","Migraine, unspecified, not intractable",9
G4391,1,G43911,"Migraine, unspecified, intractable, with status migrainosus","Migraine, unspecified, intractable, with status migrainosus","Migraine, unspecified, intractable",9
G4400,1,G44001,"Cluster headache syndrome, unspecified, intractable","Cluster headache syndrome, unspecified, intractable","Cluster headache syndrome, unspecified",9
G4401,1,G44011,"Episodic cluster headache, intractable","Episodic cluster headache, intractable",Episodic cluster headache,9
G4402,1,G44021,"Chronic cluster headache, intractable","Chronic cluster headache, intractable",Chronic cluster headache,9
G4403,1,G44031,"Episodic paroxysmal hemicrania, intractable","Episodic paroxysmal hemicrania, intractable",Episodic paroxysmal hemicrania,9
G4404,1,G44041,"Chronic paroxysmal hemicrania, intractable","Chronic paroxysmal hemicrania, intractable",Chronic paroxysmal hemicrania,9
G4405,1,G44051,"Shrt lst unil nerlgif hdache w cnjnct inject/tear, ntrct","Short lasting unilateral neuralgiform headache with conjunctival injection and tearing (SUNCT), intractable",Short lasting unilateral neuralgiform headache with conjunctival injection and tearing (SUNCT),9
G4409,1,G44091,"Other trigeminal autonomic cephalgias (TAC), intractable","Other trigeminal autonomic cephalgias (TAC), intractable",Other trigeminal autonomic cephalgias (TAC),9
G4420,1,G44201,"Tension-type headache, unspecified, intractable","Tension-type headache, unspecified, intractable","Tension-type headache, unspecified",9
G4421,1,G44211,"Episodic tension-type headache, intractable","Episodic tension-type headache, intractable",Episodic tension-type headache,9
G4422,1,G44221,"Chronic tension-type headache, intractable","Chronic tension-type headache, intractable",Chronic tension-type headache,9
G4431,1,G44311,"Acute post-traumatic headache, intractable","Acute post-traumatic headache, intractable",Acute post-traumatic headache,9
G4432,1,G44321,"Chronic post-traumatic headache, intractable","Chronic post-traumatic headache, intractable",Chronic post-traumatic headache,9
G444,1,G4441,"Drug-induced headache, not elsewhere classified, intractable","Drug-induced headache, not elsewhere classified, intractable","Drug-induced headache, not elsewhere classified",9
G445,1,G4451,Hemicrania continua,Hemicrania continua,Complicated headache syndromes,9
G448,1,G4481,Hypnic headache,Hypnic headache,Other specified headache syndromes,9
G45,1,G451,Carotid artery syndrome (hemispheric),Carotid artery syndrome (hemispheric),Transient cerebral ischemic attacks and related syndromes,9
G46,1,G461,Anterior cerebral artery syndrome,Anterior cerebral artery syndrome,Vascular syndromes of brain in cerebrovascular diseases,9
G470,1,G4701,Insomnia due to medical condition,Insomnia due to medical condition,Insomnia,9
G471,1,G4711,Idiopathic hypersomnia with long sleep time,Idiopathic hypersomnia with long sleep time,Hypersomnia,9
G472,1,G4721,"Circadian rhythm sleep disorder, delayed sleep phase type","Circadian rhythm sleep disorder, delayed sleep phase type",Circadian rhythm sleep disorders,9
G473,1,G4731,Primary central sleep apnea,Primary central sleep apnea,Sleep apnea,9
G4741,1,G47411,Narcolepsy with cataplexy,Narcolepsy with cataplexy,Narcolepsy,9
G4742,1,G47421,Narcolepsy in conditions classified elsewhere with cataplexy,Narcolepsy in conditions classified elsewhere with cataplexy,Narcolepsy in conditions classified elsewhere,9
G475,1,G4751,Confusional arousals,Confusional arousals,Parasomnia,9
G476,1,G4761,Periodic limb movement disorder,Periodic limb movement disorder,Sleep related movement disorders,9
G50,1,G501,Atypical facial pain,Atypical facial pain,Disorders of trigeminal nerve,9
G51,1,G511,Geniculate ganglionitis,Geniculate ganglionitis,Facial nerve disorders,9
G52,1,G521,Disorders of glossopharyngeal nerve,Disorders of glossopharyngeal nerve,Disorders of other cranial nerves,9
G54,1,G541,Lumbosacral plexus disorders,Lumbosacral plexus disorders,Nerve root and plexus disorders,9
G560,1,G5601,"Carpal tunnel syndrome, right upper limb","Carpal tunnel syndrome, right upper limb",Carpal tunnel syndrome,9
G561,1,G5611,"Other lesions of median nerve, right upper limb","Other lesions of median nerve, right upper limb",Other lesions of median nerve,9
G562,1,G5621,"Lesion of ulnar nerve, right upper limb","Lesion of ulnar nerve, right upper limb",Lesion of ulnar nerve,9
G563,1,G5631,"Lesion of radial nerve, right upper limb","Lesion of radial nerve, right upper limb",Lesion of radial nerve,9
G564,1,G5641,Causalgia of right upper limb,Causalgia of right upper limb,Causalgia of upper limb,9
G568,1,G5681,Other specified mononeuropathies of right upper limb,Other specified mononeuropathies of right upper limb,Other specified mononeuropathies of upper limb,9
G569,1,G5691,Unspecified mononeuropathy of right upper limb,Unspecified mononeuropathy of right upper limb,Unspecified mononeuropathy of upper limb,9
G570,1,G5701,"Lesion of sciatic nerve, right lower limb","Lesion of sciatic nerve, right lower limb",Lesion of sciatic nerve,9
G571,1,G5711,"Meralgia paresthetica, right lower limb","Meralgia paresthetica, right lower limb",Meralgia paresthetica,9
G572,1,G5721,"Lesion of femoral nerve, right lower limb","Lesion of femoral nerve, right lower limb",Lesion of femoral nerve,9
G573,1,G5731,"Lesion of lateral popliteal nerve, right lower limb","Lesion of lateral popliteal nerve, right lower limb",Lesion of lateral popliteal nerve,9
G574,1,G5741,"Lesion of medial popliteal nerve, right lower limb","Lesion of medial popliteal nerve, right lower limb",Lesion of medial popliteal nerve,9
G575,1,G5751,"Tarsal tunnel syndrome, right lower limb","Tarsal tunnel syndrome, right lower limb",Tarsal tunnel syndrome,9
G576,1,G5761,"Lesion of plantar nerve, right lower limb","Lesion of plantar nerve, right lower limb",Lesion of plantar nerve,9
G577,1,G5771,Causalgia of right lower limb,Causalgia of right lower limb,Causalgia of lower limb,9
G578,1,G5781,Other specified mononeuropathies of right lower limb,Other specified mononeuropathies of right lower limb,Other specified mononeuropathies of lower limb,9
A010,2,A0102,Typhoid fever with heart involvement,Typhoid fever with heart involvement,Typhoid fever,9
A022,2,A0222,Salmonella pneumonia,Salmonella pneumonia,Localized salmonella infections,9
A03,2,A032,Shigellosis due to Shigella boydii,Shigellosis due to Shigella boydii,Shigellosis,9
A04,2,A042,Enteroinvasive Escherichia coli infection,Enteroinvasive Escherichia coli infection,Other bacterial intestinal infections,9
A047,2,A0472,"Enterocolitis d/t Clostridium difficile, not spcf as recur","Enterocolitis due to Clostridium difficile, not specified as recurrent",Enterocolitis due to Clostridium difficile,9
A05,2,A052,Foodborne Clostridium perfringens intoxication,Foodborne Clostridium perfringens [Clostridium welchii] intoxication,"Other bacterial foodborne intoxications, not elsewhere classified",9
A06,2,A062,Amebic nondysenteric colitis,Amebic nondysenteric colitis,Amebiasis,9
A068,2,A0682,Other amebic genitourinary infections,Other amebic genitourinary infections,Amebic infection of other sites,9
A07,2,A072,Cryptosporidiosis,Cryptosporidiosis,Other protozoal intestinal diseases,9
A083,2,A0832,Astrovirus enteritis,Astrovirus enteritis,Other viral enteritis,9
A178,2,A1782,Tuberculous meningoencephalitis,Tuberculous meningoencephalitis,Other tuberculosis of nervous system,9
A180,2,A1802,Tuberculous arthritis of other joints,Tuberculous arthritis of other joints,Tuberculosis of bones and joints,9
A181,2,A1812,Tuberculosis of bladder,Tuberculosis of bladder,Tuberculosis of genitourinary system,9
A183,2,A1832,Tuberculous enteritis,Tuberculous enteritis,"Tuberculosis of intestines, peritoneum and mesenteric glands",9
A185,2,A1852,Tuberculous keratitis,Tuberculous keratitis,Tuberculosis of eye,9
A188,2,A1882,Tuberculosis of other endocrine glands,Tuberculosis of other endocrine glands,Tuberculosis of other specified organs,9
A19,2,A192,"Acute miliary tuberculosis, unspecified","Acute miliary tuberculosis, unspecified",Miliary tuberculosis,9
A20,2,A202,Pneumonic plague,Pneumonic plague,Plague,9
A21,2,A212,Pulmonary tularemia,Pulmonary tularemia,Tularemia,9
A22,2,A222,Gastrointestinal anthrax,Gastrointestinal anthrax,Anthrax,9
A23,2,A232,Brucellosis due to Brucella suis,Brucellosis due to Brucella suis,Brucellosis,9
A24,2,A242,Subacute and chronic melioidosis,Subacute and chronic melioidosis,Glanders and melioidosis,9
A28,2,A282,Extraintestinal yersiniosis,Extraintestinal yersiniosis,"Other zoonotic bacterial diseases, not elsewhere classified",9
A30,2,A302,Borderline tuberculoid leprosy,Borderline tuberculoid leprosy,Leprosy [Hansen's disease],9
A31,2,A312,Dissem mycobacterium avium-intracellulare complex (DMAC),Disseminated mycobacterium avium-intracellulare complex (DMAC),Infection due to other mycobacteria,9
A321,2,A3212,Listerial meningoencephalitis,Listerial meningoencephalitis,Listerial meningitis and meningoencephalitis,9
A328,2,A3282,Listerial endocarditis,Listerial endocarditis,Other forms of listeriosis,9
A36,2,A362,Laryngeal diphtheria,Laryngeal diphtheria,Diphtheria,9
A368,2,A3682,Diphtheritic radiculomyelitis,Diphtheritic radiculomyelitis,Other diphtheria,9
A39,2,A392,Acute meningococcemia,Acute meningococcemia,Meningococcal infection,9
A395,2,A3952,Meningococcal myocarditis,Meningococcal myocarditis,Meningococcal heart disease,9
A398,2,A3982,Meningococcal retrobulbar neuritis,Meningococcal retrobulbar neuritis,Other meningococcal infections,9
A410,2,A4102,Sepsis due to Methicillin resistant Staphylococcus aureus,Sepsis due to Methicillin resistant Staphylococcus aureus,Sepsis due to Staphylococcus aureus,9
A415,2,A4152,Sepsis due to Pseudomonas,Sepsis due to Pseudomonas,Sepsis due to other Gram-negative organisms,9
A42,2,A422,Cervicofacial actinomycosis,Cervicofacial actinomycosis,Actinomycosis,9
A428,2,A4282,Actinomycotic encephalitis,Actinomycotic encephalitis,Other forms of actinomycosis,9
A48,2,A482,Nonpneumonic Legionnaires' disease [Pontiac fever],Nonpneumonic Legionnaires' disease [Pontiac fever],"Other bacterial diseases, not elsewhere classified",9
A485,2,A4852,Wound botulism,Wound botulism,Other specified botulism,9
A490,2,A4902,"Methicillin resis staph infection, unsp site","Methicillin resistant Staphylococcus aureus infection, unspecified site","Staphylococcal infection, unspecified site",9
A500,2,A5002,Early congenital syphilitic osteochondropathy,Early congenital syphilitic osteochondropathy,"Early congenital syphilis, symptomatic",9
A503,2,A5032,Late congenital syphilitic chorioretinitis,Late congenital syphilitic chorioretinitis,Late congenital syphilitic oculopathy,9
A504,2,A5042,Late congenital syphilitic encephalitis,Late congenital syphilitic encephalitis,Late congenital neurosyphilis [juvenile neurosyphilis],9
A505,2,A5052,Hutchinson's teeth,Hutchinson's teeth,"Other late congenital syphilis, symptomatic",9
A51,2,A512,Primary syphilis of other sites,Primary syphilis of other sites,Early syphilis,9
A513,2,A5132,Syphilitic alopecia,Syphilitic alopecia,Secondary syphilis of skin and mucous membranes,9
A514,2,A5142,Secondary syphilitic female pelvic disease,Secondary syphilitic female pelvic disease,Other secondary syphilis,9
A520,2,A5202,Syphilitic aortitis,Syphilitic aortitis,Cardiovascular and cerebrovascular syphilis,9
A521,2,A5212,Other cerebrospinal syphilis,Other cerebrospinal syphilis,Symptomatic neurosyphilis,9
A527,2,A5272,Syphilis of lung and bronchus,Syphilis of lung and bronchus,Other symptomatic late syphilis,9
A540,2,A5402,"Gonococcal vulvovaginitis, unspecified","Gonococcal vulvovaginitis, unspecified",Gonococcal infection of lower genitourinary tract without periurethral or accessory gland abscess,9
A542,2,A5422,Gonococcal prostatitis,Gonococcal prostatitis,Gonococcal pelviperitonitis and other gonococcal genitourinary infection,9
A543,2,A5432,Gonococcal iridocyclitis,Gonococcal iridocyclitis,Gonococcal infection of eye,9
A544,2,A5442,Gonococcal arthritis,Gonococcal arthritis,Gonococcal infection of musculoskeletal system,9
A548,2,A5482,Gonococcal brain abscess,Gonococcal brain abscess,Other gonococcal infections,9
A560,2,A5602,Chlamydial vulvovaginitis,Chlamydial vulvovaginitis,Chlamydial infection of lower genitourinary tract,9
A590,2,A5902,Trichomonal prostatitis,Trichomonal prostatitis,Urogenital trichomoniasis,9
A600,2,A6002,Herpesviral infection of other male genital organs,Herpesviral infection of other male genital organs,Herpesviral infection of genitalia and urogenital tract,9
A66,2,A662,Other early skin lesions of yaws,Other early skin lesions of yaws,Yaws,9
A67,2,A672,Late lesions of pinta,Late lesions of pinta,Pinta [carate],9
A692,2,A6922,Other neurologic disorders in Lyme disease,Other neurologic disorders in Lyme disease,Lyme disease,9
A75,2,A752,Typhus fever due to Rickettsia typhi,Typhus fever due to Rickettsia typhi,Typhus fever,9
A77,2,A772,Spotted fever due to Rickettsia siberica,Spotted fever due to Rickettsia siberica,Spotted fever [tick-borne rickettsioses],9
A80,2,A802,"Acute paralytic poliomyelitis, wild virus, indigenous","Acute paralytic poliomyelitis, wild virus, indigenous",Acute poliomyelitis,9
A818,2,A8182,Gerstmann-Straussler-Scheinker syndrome,Gerstmann-Straussler-Scheinker syndrome,Other atypical virus infections of central nervous system,9
A83,2,A832,Eastern equine encephalitis,Eastern equine encephalitis,Mosquito-borne viral encephalitis,9
A85,2,A852,"Arthropod-borne viral encephalitis, unspecified","Arthropod-borne viral encephalitis, unspecified","Other viral encephalitis, not elsewhere classified",9
A87,2,A872,Lymphocytic choriomeningitis,Lymphocytic choriomeningitis,Viral meningitis,9
A92,2,A922,Venezuelan equine fever,Venezuelan equine fever,Other mosquito-borne viral fevers,9
A923,2,A9232,West Nile virus infection with oth neurologic manifestation,West Nile virus infection with other neurologic manifestation,West Nile virus infection,9
A93,2,A932,Colorado tick fever,Colorado tick fever,"Other arthropod-borne viral fevers, not elsewhere classified",9
A98,2,A982,Kyasanur Forest disease,Kyasanur Forest disease,"Other viral hemorrhagic fevers, not elsewhere classified",9
B00,2,B002,Herpesviral gingivostomatitis and pharyngotonsillitis,Herpesviral gingivostomatitis and pharyngotonsillitis,Herpesviral [herpes simplex] infections,9
B005,2,B0052,Herpesviral keratitis,Herpesviral keratitis,Herpesviral ocular disease,9
B008,2,B0082,Herpes simplex myelitis,Herpes simplex myelitis,Other forms of herpesviral infections,9
B011,2,B0112,Varicella myelitis,Varicella myelitis,"Varicella encephalitis, myelitis and encephalomyelitis",9
B022,2,B0222,Postherpetic trigeminal neuralgia,Postherpetic trigeminal neuralgia,Zoster with other nervous system involvement,9
B023,2,B0232,Zoster iridocyclitis,Zoster iridocyclitis,Zoster ocular disease,9
B05,2,B052,Measles complicated by pneumonia,Measles complicated by pneumonia,Measles,9
B060,2,B0602,Rubella meningitis,Rubella meningitis,Rubella with neurological complications,9
B068,2,B0682,Rubella arthritis,Rubella arthritis,Rubella with other complications,9
B082,2,B0822,Exanthema subitum [sixth disease] due to human herpesvirus 7,Exanthema subitum [sixth disease] due to human herpesvirus 7,Exanthema subitum [sixth disease],9
B086,2,B0862,Sealpox,Sealpox,Parapoxvirus infections,9
B087,2,B0872,Yaba pox virus disease,Yaba pox virus disease,Yatapoxvirus infections,9
B108,2,B1082,Human herpesvirus 7 infection,Human herpesvirus 7 infection,Other human herpesvirus infection,9
B16,2,B162,Acute hepatitis B without delta-agent with hepatic coma,Acute hepatitis B without delta-agent with hepatic coma,Acute hepatitis B,9
B18,2,B182,Chronic viral hepatitis C,Chronic viral hepatitis C,Chronic viral hepatitis,9
B25,2,B252,Cytomegaloviral pancreatitis,Cytomegaloviral pancreatitis,Cytomegaloviral disease,9
B26,2,B262,Mumps encephalitis,Mumps encephalitis,Mumps,9
B268,2,B2682,Mumps myocarditis,Mumps myocarditis,Mumps with other complications,9
B270,2,B2702,Gammaherpesviral mononucleosis with meningitis,Gammaherpesviral mononucleosis with meningitis,Gammaherpesviral mononucleosis,9
B271,2,B2712,Cytomegaloviral mononucleosis with meningitis,Cytomegaloviral mononucleosis with meningitis,Cytomegaloviral mononucleosis,9
B278,2,B2782,Other infectious mononucleosis with meningitis,Other infectious mononucleosis with meningitis,Other infectious mononucleosis,9
B279,2,B2792,"Infectious mononucleosis, unspecified with meningitis","Infectious mononucleosis, unspecified with meningitis","Infectious mononucleosis, unspecified",9
B30,2,B302,Viral pharyngoconjunctivitis,Viral pharyngoconjunctivitis,Viral conjunctivitis,9
B332,2,B3322,Viral myocarditis,Viral myocarditis,Viral carditis,9
B34,2,B342,"Coronavirus infection, unspecified","Coronavirus infection, unspecified",Viral infection of unspecified site,9
B35,2,B352,Tinea manuum,Tinea manuum,Dermatophytosis,9
B36,2,B362,White piedra,White piedra,Other superficial mycoses,9
B37,2,B372,Candidiasis of skin and nail,Candidiasis of skin and nail,Candidiasis,9
B374,2,B3742,Candidal balanitis,Candidal balanitis,Candidiasis of other urogenital sites,9
B378,2,B3782,Candidal enteritis,Candidal enteritis,Candidiasis of other sites,9
B38,2,B382,"Pulmonary coccidioidomycosis, unspecified","Pulmonary coccidioidomycosis, unspecified",Coccidioidomycosis,9
B39,2,B392,"Pulmonary histoplasmosis capsulati, unspecified","Pulmonary histoplasmosis capsulati, unspecified",Histoplasmosis,9
B40,2,B402,"Pulmonary blastomycosis, unspecified","Pulmonary blastomycosis, unspecified",Blastomycosis,9
B428,2,B4282,Sporotrichosis arthritis,Sporotrichosis arthritis,Other forms of sporotrichosis,9
B43,2,B432,Subcutaneous pheomycotic abscess and cyst,Subcutaneous pheomycotic abscess and cyst,Chromomycosis and pheomycotic abscess,9
B44,2,B442,Tonsillar aspergillosis,Tonsillar aspergillosis,Aspergillosis,9
B45,2,B452,Cutaneous cryptococcosis,Cutaneous cryptococcosis,Cryptococcosis,9
B46,2,B462,Gastrointestinal mucormycosis,Gastrointestinal mucormycosis,Zygomycosis,9
B48,2,B482,Allescheriasis,Allescheriasis,"Other mycoses, not elsewhere classified",9
B55,2,B552,Mucocutaneous leishmaniasis,Mucocutaneous leishmaniasis,Leishmaniasis,9
B57,2,B572,Chagas' disease (chronic) with heart involvement,Chagas' disease (chronic) with heart involvement,Chagas' disease,9
B573,2,B5732,Megacolon in Chagas' disease,Megacolon in Chagas' disease,Chagas' disease (chronic) with digestive system involvement,9
B574,2,B5742,Meningoencephalitis in Chagas' disease,Meningoencephalitis in Chagas' disease,Chagas' disease (chronic) with nervous system involvement,9
B588,2,B5882,Toxoplasma myositis,Toxoplasma myositis,Toxoplasmosis with other organ involvement,9
B601,2,B6012,Conjunctivitis due to Acanthamoeba,Conjunctivitis due to Acanthamoeba,Acanthamebiasis,9
B65,2,B652,Schistosomiasis due to Schistosoma japonicum,Schistosomiasis due to Schistosoma japonicum,Schistosomiasis [bilharziasis],9
B66,2,B662,Dicroceliasis,Dicroceliasis,Other fluke infections,9
B67,2,B672,Echinococcus granulosus infection of bone,Echinococcus granulosus infection of bone,Echinococcosis,9
B673,2,B6732,"Echinococcus granulosus infection, multiple sites","Echinococcus granulosus infection, multiple sites","Echinococcus granulosus infection, other and multiple sites",9
B730,2,B7302,Onchocerciasis with glaucoma,Onchocerciasis with glaucoma,Onchocerciasis with eye disease,9
B74,2,B742,Filariasis due to Brugia timori,Filariasis due to Brugia timori,Filariasis,9
B81,2,B812,Trichostrongyliasis,Trichostrongyliasis,"Other intestinal helminthiases, not elsewhere classified",9
B83,2,B832,Angiostrongyliasis due to Parastrongylus cantonensis,Angiostrongyliasis due to Parastrongylus cantonensis,Other helminthiases,9
B85,2,B852,"Pediculosis, unspecified","Pediculosis, unspecified",Pediculosis and phthiriasis,9
B87,2,B872,Ocular myiasis,Ocular myiasis,Myiasis,9
B878,2,B8782,Intestinal myiasis,Intestinal myiasis,Myiasis of other sites,9
B66,4,B664,Paragonimiasis,Paragonimiasis,Other fluke infections,9
B90,2,B902,Sequelae of tuberculosis of bones and joints,Sequelae of tuberculosis of bones and joints,Sequelae of tuberculosis,9
B94,2,B942,Sequelae of viral hepatitis,Sequelae of viral hepatitis,Sequelae of other and unspecified infectious and parasitic diseases,9
B95,2,B952,Enterococcus as the cause of diseases classified elsewhere,Enterococcus as the cause of diseases classified elsewhere,"Streptococcus, Staphylococcus, and Enterococcus as the cause of diseases classified elsewhere",9
B956,2,B9562,Methicillin resis staph infct causing diseases classd elswhr,Methicillin resistant Staphylococcus aureus infection as the cause of diseases classified elsewhere,Staphylococcus aureus as the cause of diseases classified elsewhere,9
B962,2,B9622,Oth shiga toxin E coli (STEC) causing diseases classd elswhr,Other specified Shiga toxin-producing Escherichia coli [E. coli] (STEC) as the cause of diseases classified elsewhere,Escherichia coli [E. coli ] as the cause of diseases classified elsewhere,9
B968,2,B9682,Vibrio vulnificus as the cause of diseases classd elswhr,Vibrio vulnificus as the cause of diseases classified elsewhere,Other specified bacterial agents as the cause of diseases classified elsewhere,9
B971,2,B9712,Echovirus as the cause of diseases classified elsewhere,Echovirus as the cause of diseases classified elsewhere,Enterovirus as the cause of diseases classified elsewhere,9
B973,2,B9732,Oncovirus as the cause of diseases classified elsewhere,Oncovirus as the cause of diseases classified elsewhere,Retrovirus as the cause of diseases classified elsewhere,9
C00,2,C002,"Malignant neoplasm of external lip, unspecified","Malignant neoplasm of external lip, unspecified",Malignant neoplasm of lip,9
C02,2,C022,Malignant neoplasm of ventral surface of tongue,Malignant neoplasm of ventral surface of tongue,Malignant neoplasm of other and unspecified parts of tongue,9
C05,2,C052,Malignant neoplasm of uvula,Malignant neoplasm of uvula,Malignant neoplasm of palate,9
C06,2,C062,Malignant neoplasm of retromolar area,Malignant neoplasm of retromolar area,Malignant neoplasm of other and unspecified parts of mouth,9
C10,2,C102,Malignant neoplasm of lateral wall of oropharynx,Malignant neoplasm of lateral wall of oropharynx,Malignant neoplasm of oropharynx,9
C11,2,C112,Malignant neoplasm of lateral wall of nasopharynx,Malignant neoplasm of lateral wall of nasopharynx,Malignant neoplasm of nasopharynx,9
C13,2,C132,Malignant neoplasm of posterior wall of hypopharynx,Malignant neoplasm of posterior wall of hypopharynx,Malignant neoplasm of hypopharynx,9
C14,2,C142,Malignant neoplasm of Waldeyer's ring,Malignant neoplasm of Waldeyer's ring,"Malignant neoplasm of other and ill-defined sites in the lip, oral cavity and pharynx",9
C16,2,C162,Malignant neoplasm of body of stomach,Malignant neoplasm of body of stomach,Malignant neoplasm of stomach,9
C17,2,C172,Malignant neoplasm of ileum,Malignant neoplasm of ileum,Malignant neoplasm of small intestine,9
C18,2,C182,Malignant neoplasm of ascending colon,Malignant neoplasm of ascending colon,Malignant neoplasm of colon,9
C21,2,C212,Malignant neoplasm of cloacogenic zone,Malignant neoplasm of cloacogenic zone,Malignant neoplasm of anus and anal canal,9
C22,2,C222,Hepatoblastoma,Hepatoblastoma,Malignant neoplasm of liver and intrahepatic bile ducts,9
C25,2,C252,Malignant neoplasm of tail of pancreas,Malignant neoplasm of tail of pancreas,Malignant neoplasm of pancreas,9
C31,2,C312,Malignant neoplasm of frontal sinus,Malignant neoplasm of frontal sinus,Malignant neoplasm of accessory sinuses,9
C32,2,C322,Malignant neoplasm of subglottis,Malignant neoplasm of subglottis,Malignant neoplasm of larynx,9
C340,2,C3402,Malignant neoplasm of left main bronchus,Malignant neoplasm of left main bronchus,Malignant neoplasm of main bronchus,9
C341,2,C3412,"Malignant neoplasm of upper lobe, left bronchus or lung","Malignant neoplasm of upper lobe, left bronchus or lung","Malignant neoplasm of upper lobe, bronchus or lung",9
C343,2,C3432,"Malignant neoplasm of lower lobe, left bronchus or lung","Malignant neoplasm of lower lobe, left bronchus or lung","Malignant neoplasm of lower lobe, bronchus or lung",9
C348,2,C3482,Malignant neoplasm of ovrlp sites of left bronchus and lung,Malignant neoplasm of overlapping sites of left bronchus and lung,Malignant neoplasm of overlapping sites of bronchus and lung,9
C349,2,C3492,Malignant neoplasm of unsp part of left bronchus or lung,Malignant neoplasm of unspecified part of left bronchus or lung,Malignant neoplasm of unspecified part of bronchus or lung,9
C38,2,C382,Malignant neoplasm of posterior mediastinum,Malignant neoplasm of posterior mediastinum,"Malignant neoplasm of heart, mediastinum and pleura",9
C400,2,C4002,Malig neoplasm of scapula and long bones of left upper limb,Malignant neoplasm of scapula and long bones of left upper limb,Malignant neoplasm of scapula and long bones of upper limb,9
C401,2,C4012,Malignant neoplasm of short bones of left upper limb,Malignant neoplasm of short bones of left upper limb,Malignant neoplasm of short bones of upper limb,9
C402,2,C4022,Malignant neoplasm of long bones of left lower limb,Malignant neoplasm of long bones of left lower limb,Malignant neoplasm of long bones of lower limb,9
C403,2,C4032,Malignant neoplasm of short bones of left lower limb,Malignant neoplasm of short bones of left lower limb,Malignant neoplasm of short bones of lower limb,9
C408,2,C4082,Malig neoplm of ovrlp sites of bone/artic cartl of left limb,Malignant neoplasm of overlapping sites of bone and articular cartilage of left limb,Malignant neoplasm of overlapping sites of bone and articular cartilage of limb,9
C409,2,C4092,Malig neoplasm of unsp bones and artic cartlg of left limb,Malignant neoplasm of unspecified bones and articular cartilage of left limb,Malignant neoplasm of unspecified bones and articular cartilage of limb,9
C41,2,C412,Malignant neoplasm of vertebral column,Malignant neoplasm of vertebral column,Malignant neoplasm of bone and articular cartilage of other and unspecified sites,9
C431,2,C4312,"Malignant melanoma of left eyelid, including canthus","Malignant melanoma of left eyelid, including canthus","Malignant melanoma of eyelid, including canthus",9
C432,2,C4322,Malignant melanoma of left ear and external auricular canal,Malignant melanoma of left ear and external auricular canal,Malignant melanoma of ear and external auricular canal,9
C435,2,C4352,Malignant melanoma of skin of breast,Malignant melanoma of skin of breast,Malignant melanoma of trunk,9
B74,4,B744,Mansonelliasis,Mansonelliasis,Filariasis,9
C436,2,C4362,"Malignant melanoma of left upper limb, including shoulder","Malignant melanoma of left upper limb, including shoulder","Malignant melanoma of upper limb, including shoulder",9
C437,2,C4372,"Malignant melanoma of left lower limb, including hip","Malignant melanoma of left lower limb, including hip","Malignant melanoma of lower limb, including hip",9
C4A1,2,C4A12,"Merkel cell carcinoma of left eyelid, including canthus","Merkel cell carcinoma of left eyelid, including canthus","Merkel cell carcinoma of eyelid, including canthus",9
C4A2,2,C4A22,Merkel cell carcinoma of left ear and external auric canal,Merkel cell carcinoma of left ear and external auricular canal,Merkel cell carcinoma of ear and external auricular canal,9
C4A5,2,C4A52,Merkel cell carcinoma of skin of breast,Merkel cell carcinoma of skin of breast,Merkel cell carcinoma of trunk,9
C4A6,2,C4A62,"Merkel cell carcinoma of left upper limb, including shoulder","Merkel cell carcinoma of left upper limb, including shoulder","Merkel cell carcinoma of upper limb, including shoulder",9
C4A7,2,C4A72,"Merkel cell carcinoma of left lower limb, including hip","Merkel cell carcinoma of left lower limb, including hip","Merkel cell carcinoma of lower limb, including hip",9
C440,2,C4402,Squamous cell carcinoma of skin of lip,Squamous cell carcinoma of skin of lip,Other and unspecified malignant neoplasm of skin of lip,9
C4410,2,C44102,"Unsp malignant neoplasm skin/ right eyelid, inc canthus","Unspecified malignant neoplasm of skin of right eyelid, including canthus","Unspecified malignant neoplasm of skin of eyelid, including canthus",9
C4411,2,C44112,"Basal cell carcinoma skin/ right eyelid, including canthus","Basal cell carcinoma of skin of right eyelid, including canthus","Basal cell carcinoma of skin of eyelid, including canthus",9
C4412,2,C44122,"Squamous cell carcinoma skin/ right eyelid, inc canthus","Squamous cell carcinoma of skin of right eyelid, including canthus","Squamous cell carcinoma of skin of eyelid, including canthus",9
C4419,2,C44192,"Oth malignant neoplasm skin/ right eyelid, including canthus","Other specified malignant neoplasm of skin of right eyelid, including canthus","Other specified malignant neoplasm of skin of eyelid, including canthus",9
C4420,2,C44202,Unsp malig neoplasm skin/ right ear and external auric canal,Unspecified malignant neoplasm of skin of right ear and external auricular canal,Unspecified malignant neoplasm of skin of ear and external auricular canal,9
C4421,2,C44212,Basal cell carcinoma skin/ r ear and external auric canal,Basal cell carcinoma of skin of right ear and external auricular canal,Basal cell carcinoma of skin of ear and external auricular canal,9
C4422,2,C44222,Squamous cell carcinoma skin/ r ear and external auric canal,Squamous cell carcinoma of skin of right ear and external auricular canal,Squamous cell carcinoma of skin of ear and external auricular canal,9
C4429,2,C44292,Oth malig neoplasm skin/ right ear and external auric canal,Other specified malignant neoplasm of skin of right ear and external auricular canal,Other specified malignant neoplasm of skin of ear and external auricular canal,9
C444,2,C4442,Squamous cell carcinoma of skin of scalp and neck,Squamous cell carcinoma of skin of scalp and neck,Other and unspecified malignant neoplasm of skin of scalp and neck,9
C4460,2,C44602,"Unsp malignant neoplasm skin/ right upper limb, inc shoulder","Unspecified malignant neoplasm of skin of right upper limb, including shoulder","Unspecified malignant neoplasm of skin of upper limb, including shoulder",9
C4461,2,C44612,"Basal cell carcinoma skin/ right upper limb, inc shoulder","Basal cell carcinoma of skin of right upper limb, including shoulder","Basal cell carcinoma of skin of upper limb, including shoulder",9
C4462,2,C44622,"Squamous cell carcinoma skin/ right upper limb, inc shoulder","Squamous cell carcinoma of skin of right upper limb, including shoulder","Squamous cell carcinoma of skin of upper limb, including shoulder",9
C4469,2,C44692,"Oth malignant neoplasm skin/ right upper limb, inc shoulder","Other specified malignant neoplasm of skin of right upper limb, including shoulder","Other specified malignant neoplasm of skin of upper limb, including shoulder",9
C4470,2,C44702,"Unsp malignant neoplasm skin/ right lower limb, inc hip","Unspecified malignant neoplasm of skin of right lower limb, including hip","Unspecified malignant neoplasm of skin of lower limb, including hip",9
C4471,2,C44712,"Basal cell carcinoma skin/ right lower limb, including hip","Basal cell carcinoma of skin of right lower limb, including hip","Basal cell carcinoma of skin of lower limb, including hip",9
C4472,2,C44722,"Squamous cell carcinoma skin/ right lower limb, inc hip","Squamous cell carcinoma of skin of right lower limb, including hip","Squamous cell carcinoma of skin of lower limb, including hip",9
C4479,2,C44792,"Oth malignant neoplasm skin/ right lower limb, including hip","Other specified malignant neoplasm of skin of right lower limb, including hip","Other specified malignant neoplasm of skin of lower limb, including hip",9
C448,2,C4482,Squamous cell carcinoma of overlapping sites of skin,Squamous cell carcinoma of overlapping sites of skin,Other and unspecified malignant neoplasm of overlapping sites of skin,9
C449,2,C4492,"Squamous cell carcinoma of skin, unspecified","Squamous cell carcinoma of skin, unspecified","Other and unspecified malignant neoplasm of skin, unspecified",9
C45,2,C452,Mesothelioma of pericardium,Mesothelioma of pericardium,Mesothelioma,9
C46,2,C462,Kaposi's sarcoma of palate,Kaposi's sarcoma of palate,Kaposi's sarcoma,9
C465,2,C4652,Kaposi's sarcoma of left lung,Kaposi's sarcoma of left lung,Kaposi's sarcoma of lung,9
C471,2,C4712,"Malig neoplm of prph nerves of left upper limb, inc shoulder","Malignant neoplasm of peripheral nerves of left upper limb, including shoulder","Malignant neoplasm of peripheral nerves of upper limb, including shoulder",9
C472,2,C4722,"Malig neoplasm of prph nerves of left lower limb, inc hip","Malignant neoplasm of peripheral nerves of left lower limb, including hip","Malignant neoplasm of peripheral nerves of lower limb, including hip",9
C48,2,C482,"Malignant neoplasm of peritoneum, unspecified","Malignant neoplasm of peritoneum, unspecified",Malignant neoplasm of retroperitoneum and peritoneum,9
C491,2,C4912,"Malig neoplm of conn and soft tiss of l upr limb, inc shldr","Malignant neoplasm of connective and soft tissue of left upper limb, including shoulder","Malignant neoplasm of connective and soft tissue of upper limb, including shoulder",9
C492,2,C4922,"Malig neoplm of conn and soft tiss of left low limb, inc hip","Malignant neoplasm of connective and soft tissue of left lower limb, including hip","Malignant neoplasm of connective and soft tissue of lower limb, including hip",9
C49A,2,C49A2,Gastrointestinal stromal tumor of stomach,Gastrointestinal stromal tumor of stomach,Gastrointestinal stromal tumor,9
C5001,2,C50012,"Malignant neoplasm of nipple and areola, left female breast","Malignant neoplasm of nipple and areola, left female breast","Malignant neoplasm of nipple and areola, female",9
C5002,2,C50022,"Malignant neoplasm of nipple and areola, left male breast","Malignant neoplasm of nipple and areola, left male breast","Malignant neoplasm of nipple and areola, male",9
C5011,2,C50112,Malignant neoplasm of central portion of left female breast,Malignant neoplasm of central portion of left female breast,"Malignant neoplasm of central portion of breast, female",9
C5012,2,C50122,Malignant neoplasm of central portion of left male breast,Malignant neoplasm of central portion of left male breast,"Malignant neoplasm of central portion of breast, male",9
C5021,2,C50212,Malig neoplasm of upper-inner quadrant of left female breast,Malignant neoplasm of upper-inner quadrant of left female breast,"Malignant neoplasm of upper-inner quadrant of breast, female",9
C5022,2,C50222,Malig neoplasm of upper-inner quadrant of left male breast,Malignant neoplasm of upper-inner quadrant of left male breast,"Malignant neoplasm of upper-inner quadrant of breast, male",9
C5031,2,C50312,Malig neoplasm of lower-inner quadrant of left female breast,Malignant neoplasm of lower-inner quadrant of left female breast,"Malignant neoplasm of lower-inner quadrant of breast, female",9
C5032,2,C50322,Malig neoplasm of lower-inner quadrant of left male breast,Malignant neoplasm of lower-inner quadrant of left male breast,"Malignant neoplasm of lower-inner quadrant of breast, male",9
C5041,2,C50412,Malig neoplasm of upper-outer quadrant of left female breast,Malignant neoplasm of upper-outer quadrant of left female breast,"Malignant neoplasm of upper-outer quadrant of breast, female",9
C5042,2,C50422,Malig neoplasm of upper-outer quadrant of left male breast,Malignant neoplasm of upper-outer quadrant of left male breast,"Malignant neoplasm of upper-outer quadrant of breast, male",9
C5051,2,C50512,Malig neoplasm of lower-outer quadrant of left female breast,Malignant neoplasm of lower-outer quadrant of left female breast,"Malignant neoplasm of lower-outer quadrant of breast, female",9
C5052,2,C50522,Malig neoplasm of lower-outer quadrant of left male breast,Malignant neoplasm of lower-outer quadrant of left male breast,"Malignant neoplasm of lower-outer quadrant of breast, male",9
C5061,2,C50612,Malignant neoplasm of axillary tail of left female breast,Malignant neoplasm of axillary tail of left female breast,"Malignant neoplasm of axillary tail of breast, female",9
C5062,2,C50622,Malignant neoplasm of axillary tail of left male breast,Malignant neoplasm of axillary tail of left male breast,"Malignant neoplasm of axillary tail of breast, male",9
C5081,2,C50812,Malignant neoplasm of ovrlp sites of left female breast,Malignant neoplasm of overlapping sites of left female breast,"Malignant neoplasm of overlapping sites of breast, female",9
C5082,2,C50822,Malignant neoplasm of overlapping sites of left male breast,Malignant neoplasm of overlapping sites of left male breast,"Malignant neoplasm of overlapping sites of breast, male",9
C5091,2,C50912,Malignant neoplasm of unspecified site of left female breast,Malignant neoplasm of unspecified site of left female breast,"Malignant neoplasm of breast of unspecified site, female",9
C5092,2,C50922,Malignant neoplasm of unspecified site of left male breast,Malignant neoplasm of unspecified site of left male breast,"Malignant neoplasm of breast of unspecified site, male",9
C51,2,C512,Malignant neoplasm of clitoris,Malignant neoplasm of clitoris,Malignant neoplasm of vulva,9
C54,2,C542,Malignant neoplasm of myometrium,Malignant neoplasm of myometrium,Malignant neoplasm of corpus uteri,9
C56,2,C562,Malignant neoplasm of left ovary,Malignant neoplasm of left ovary,Malignant neoplasm of ovary,9
C570,2,C5702,Malignant neoplasm of left fallopian tube,Malignant neoplasm of left fallopian tube,Malignant neoplasm of fallopian tube,9
C571,2,C5712,Malignant neoplasm of left broad ligament,Malignant neoplasm of left broad ligament,Malignant neoplasm of broad ligament,9
C572,2,C5722,Malignant neoplasm of left round ligament,Malignant neoplasm of left round ligament,Malignant neoplasm of round ligament,9
C60,2,C602,Malignant neoplasm of body of penis,Malignant neoplasm of body of penis,Malignant neoplasm of penis,9
C620,2,C6202,Malignant neoplasm of undescended left testis,Malignant neoplasm of undescended left testis,Malignant neoplasm of undescended testis,9
C621,2,C6212,Malignant neoplasm of descended left testis,Malignant neoplasm of descended left testis,Malignant neoplasm of descended testis,9
C629,2,C6292,"Malig neoplasm of left testis, unsp descended or undescended","Malignant neoplasm of left testis, unspecified whether descended or undescended","Malignant neoplasm of testis, unspecified whether descended or undescended",9
C630,2,C6302,Malignant neoplasm of left epididymis,Malignant neoplasm of left epididymis,Malignant neoplasm of epididymis,9
C631,2,C6312,Malignant neoplasm of left spermatic cord,Malignant neoplasm of left spermatic cord,Malignant neoplasm of spermatic cord,9
C64,2,C642,"Malignant neoplasm of left kidney, except renal pelvis","Malignant neoplasm of left kidney, except renal pelvis","Malignant neoplasm of kidney, except renal pelvis",9
C65,2,C652,Malignant neoplasm of left renal pelvis,Malignant neoplasm of left renal pelvis,Malignant neoplasm of renal pelvis,9
C66,2,C662,Malignant neoplasm of left ureter,Malignant neoplasm of left ureter,Malignant neoplasm of ureter,9
C67,2,C672,Malignant neoplasm of lateral wall of bladder,Malignant neoplasm of lateral wall of bladder,Malignant neoplasm of bladder,9
C690,2,C6902,Malignant neoplasm of left conjunctiva,Malignant neoplasm of left conjunctiva,Malignant neoplasm of conjunctiva,9
C691,2,C6912,Malignant neoplasm of left cornea,Malignant neoplasm of left cornea,Malignant neoplasm of cornea,9
C692,2,C6922,Malignant neoplasm of left retina,Malignant neoplasm of left retina,Malignant neoplasm of retina,9
C693,2,C6932,Malignant neoplasm of left choroid,Malignant neoplasm of left choroid,Malignant neoplasm of choroid,9
C694,2,C6942,Malignant neoplasm of left ciliary body,Malignant neoplasm of left ciliary body,Malignant neoplasm of ciliary body,9
C695,2,C6952,Malignant neoplasm of left lacrimal gland and duct,Malignant neoplasm of left lacrimal gland and duct,Malignant neoplasm of lacrimal gland and duct,9
C696,2,C6962,Malignant neoplasm of left orbit,Malignant neoplasm of left orbit,Malignant neoplasm of orbit,9
C698,2,C6982,Malignant neoplasm of ovrlp sites of left eye and adnexa,Malignant neoplasm of overlapping sites of left eye and adnexa,Malignant neoplasm of overlapping sites of eye and adnexa,9
C699,2,C6992,Malignant neoplasm of unspecified site of left eye,Malignant neoplasm of unspecified site of left eye,Malignant neoplasm of unspecified site of eye,9
C71,2,C712,Malignant neoplasm of temporal lobe,Malignant neoplasm of temporal lobe,Malignant neoplasm of brain,9
C722,2,C7222,Malignant neoplasm of left olfactory nerve,Malignant neoplasm of left olfactory nerve,Malignant neoplasm of olfactory nerve,9
C723,2,C7232,Malignant neoplasm of left optic nerve,Malignant neoplasm of left optic nerve,Malignant neoplasm of optic nerve,9
C724,2,C7242,Malignant neoplasm of left acoustic nerve,Malignant neoplasm of left acoustic nerve,Malignant neoplasm of acoustic nerve,9
C740,2,C7402,Malignant neoplasm of cortex of left adrenal gland,Malignant neoplasm of cortex of left adrenal gland,Malignant neoplasm of cortex of adrenal gland,9
C741,2,C7412,Malignant neoplasm of medulla of left adrenal gland,Malignant neoplasm of medulla of left adrenal gland,Malignant neoplasm of medulla of adrenal gland,9
C749,2,C7492,Malignant neoplasm of unspecified part of left adrenal gland,Malignant neoplasm of unspecified part of left adrenal gland,Malignant neoplasm of unspecified part of adrenal gland,9
C75,2,C752,Malignant neoplasm of craniopharyngeal duct,Malignant neoplasm of craniopharyngeal duct,Malignant neoplasm of other endocrine glands and related structures,9
C7A01,2,C7A012,Malignant carcinoid tumor of the ileum,Malignant carcinoid tumor of the ileum,Malignant carcinoid tumors of the small intestine,9
C7A02,2,C7A022,Malignant carcinoid tumor of the ascending colon,Malignant carcinoid tumor of the ascending colon,"Malignant carcinoid tumors of the appendix, large intestine, and rectum",9
C7A09,2,C7A092,Malignant carcinoid tumor of the stomach,Malignant carcinoid tumor of the stomach,Malignant carcinoid tumors of other sites,9
C7B0,2,C7B02,Secondary carcinoid tumors of liver,Secondary carcinoid tumors of liver,Secondary carcinoid tumors,9
C76,2,C762,Malignant neoplasm of abdomen,Malignant neoplasm of abdomen,Malignant neoplasm of other and ill-defined sites,9
C764,2,C7642,Malignant neoplasm of left upper limb,Malignant neoplasm of left upper limb,Malignant neoplasm of upper limb,9
C765,2,C7652,Malignant neoplasm of left lower limb,Malignant neoplasm of left lower limb,Malignant neoplasm of lower limb,9
C77,2,C772,Secondary and unsp malignant neoplasm of intra-abd nodes,Secondary and unspecified malignant neoplasm of intra-abdominal lymph nodes,Secondary and unspecified malignant neoplasm of lymph nodes,9
C780,2,C7802,Secondary malignant neoplasm of left lung,Secondary malignant neoplasm of left lung,Secondary malignant neoplasm of lung,9
C790,2,C7902,Secondary malignant neoplasm of left kidney and renal pelvis,Secondary malignant neoplasm of left kidney and renal pelvis,Secondary malignant neoplasm of kidney and renal pelvis,9
C793,2,C7932,Secondary malignant neoplasm of cerebral meninges,Secondary malignant neoplasm of cerebral meninges,Secondary malignant neoplasm of brain and cerebral meninges,9
C795,2,C7952,Secondary malignant neoplasm of bone marrow,Secondary malignant neoplasm of bone marrow,Secondary malignant neoplasm of bone and bone marrow,9
C796,2,C7962,Secondary malignant neoplasm of left ovary,Secondary malignant neoplasm of left ovary,Secondary malignant neoplasm of ovary,9
C797,2,C7972,Secondary malignant neoplasm of left adrenal gland,Secondary malignant neoplasm of left adrenal gland,Secondary malignant neoplasm of adrenal gland,9
C798,2,C7982,Secondary malignant neoplasm of genital organs,Secondary malignant neoplasm of genital organs,Secondary malignant neoplasm of other specified sites,9
C80,2,C802,Malignant neoplasm associated with transplanted organ,Malignant neoplasm associated with transplanted organ,Malignant neoplasm without specification of site,9
C810,2,C8102,"Nodular lymphocy predom Hodgkin lymphoma, intrathorac nodes","Nodular lymphocyte predominant Hodgkin lymphoma, intrathoracic lymph nodes",Nodular lymphocyte predominant Hodgkin lymphoma,9
C811,2,C8112,"Nodular sclerosis Hodgkin lymphoma, intrathorac lymph nodes","Nodular sclerosis Hodgkin lymphoma, intrathoracic lymph nodes",Nodular sclerosis Hodgkin lymphoma,9
C812,2,C8122,"Mixed cellularity Hodgkin lymphoma, intrathorac lymph nodes","Mixed cellularity Hodgkin lymphoma, intrathoracic lymph nodes",Mixed cellularity Hodgkin lymphoma,9
C813,2,C8132,"Lymphocyte depleted Hodgkin lymphoma, intrathorac nodes","Lymphocyte depleted Hodgkin lymphoma, intrathoracic lymph nodes",Lymphocyte depleted Hodgkin lymphoma,9
C814,2,C8142,"Lymphocyte-rich Hodgkin lymphoma, intrathoracic lymph nodes","Lymphocyte-rich Hodgkin lymphoma, intrathoracic lymph nodes",Lymphocyte-rich Hodgkin lymphoma,9
C817,2,C8172,"Other Hodgkin lymphoma, intrathoracic lymph nodes","Other Hodgkin lymphoma, intrathoracic lymph nodes",Other Hodgkin lymphoma,9
C819,2,C8192,"Hodgkin lymphoma, unspecified, intrathoracic lymph nodes","Hodgkin lymphoma, unspecified, intrathoracic lymph nodes","Hodgkin lymphoma, unspecified",9
C820,2,C8202,"Follicular lymphoma grade I, intrathoracic lymph nodes","Follicular lymphoma grade I, intrathoracic lymph nodes",Follicular lymphoma grade I,9
C821,2,C8212,"Follicular lymphoma grade II, intrathoracic lymph nodes","Follicular lymphoma grade II, intrathoracic lymph nodes",Follicular lymphoma grade II,9
C822,2,C8222,"Follicular lymphoma grade III, unsp, intrathorac lymph nodes","Follicular lymphoma grade III, unspecified, intrathoracic lymph nodes","Follicular lymphoma grade III, unspecified",9
C823,2,C8232,"Follicular lymphoma grade IIIa, intrathoracic lymph nodes","Follicular lymphoma grade IIIa, intrathoracic lymph nodes",Follicular lymphoma grade IIIa,9
C824,2,C8242,"Follicular lymphoma grade IIIb, intrathoracic lymph nodes","Follicular lymphoma grade IIIb, intrathoracic lymph nodes",Follicular lymphoma grade IIIb,9
C825,2,C8252,"Diffuse follicle center lymphoma, intrathoracic lymph nodes","Diffuse follicle center lymphoma, intrathoracic lymph nodes",Diffuse follicle center lymphoma,9
C826,2,C8262,"Cutaneous follicle center lymphoma, intrathorac lymph nodes","Cutaneous follicle center lymphoma, intrathoracic lymph nodes",Cutaneous follicle center lymphoma,9
D868,4,D8684,Sarcoid pyelonephritis,Sarcoid pyelonephritis,Sarcoidosis of other sites,9
C828,2,C8282,"Oth types of follicular lymphoma, intrathoracic lymph nodes","Other types of follicular lymphoma, intrathoracic lymph nodes",Other types of follicular lymphoma,9
C829,2,C8292,"Follicular lymphoma, unspecified, intrathoracic lymph nodes","Follicular lymphoma, unspecified, intrathoracic lymph nodes","Follicular lymphoma, unspecified",9
C830,2,C8302,"Small cell B-cell lymphoma, intrathoracic lymph nodes","Small cell B-cell lymphoma, intrathoracic lymph nodes",Small cell B-cell lymphoma,9
C831,2,C8312,"Mantle cell lymphoma, intrathoracic lymph nodes","Mantle cell lymphoma, intrathoracic lymph nodes",Mantle cell lymphoma,9
C833,2,C8332,"Diffuse large B-cell lymphoma, intrathoracic lymph nodes","Diffuse large B-cell lymphoma, intrathoracic lymph nodes",Diffuse large B-cell lymphoma,9
C835,2,C8352,"Lymphoblastic (diffuse) lymphoma, intrathoracic lymph nodes","Lymphoblastic (diffuse) lymphoma, intrathoracic lymph nodes",Lymphoblastic (diffuse) lymphoma,9
C837,2,C8372,"Burkitt lymphoma, intrathoracic lymph nodes","Burkitt lymphoma, intrathoracic lymph nodes",Burkitt lymphoma,9
C838,2,C8382,"Other non-follicular lymphoma, intrathoracic lymph nodes","Other non-follicular lymphoma, intrathoracic lymph nodes",Other non-follicular lymphoma,9
C839,2,C8392,"Non-follic (diffuse) lymphoma, unsp, intrathorac lymph nodes","Non-follicular (diffuse) lymphoma, unspecified, intrathoracic lymph nodes","Non-follicular (diffuse) lymphoma, unspecified",9
C840,2,C8402,"Mycosis fungoides, intrathoracic lymph nodes","Mycosis fungoides, intrathoracic lymph nodes",Mycosis fungoides,9
C841,2,C8412,"Sezary disease, intrathoracic lymph nodes","Sezary disease, intrathoracic lymph nodes",Sezary disease,9
C844,2,C8442,"Peripheral T-cell lymphoma, not class, intrathorac nodes","Peripheral T-cell lymphoma, not classified, intrathoracic lymph nodes","Peripheral T-cell lymphoma, not classified",9
C846,2,C8462,"Anaplastic large cell lymphoma, ALK-pos, intrathorac nodes","Anaplastic large cell lymphoma, ALK-positive, intrathoracic lymph nodes","Anaplastic large cell lymphoma, ALK-positive",9
C847,2,C8472,"Anaplastic large cell lymphoma, ALK-neg, intrathorac nodes","Anaplastic large cell lymphoma, ALK-negative, intrathoracic lymph nodes","Anaplastic large cell lymphoma, ALK-negative",9
C84A,2,C84A2,"Cutaneous T-cell lymphoma, unsp, intrathoracic lymph nodes","Cutaneous T-cell lymphoma, unspecified, intrathoracic lymph nodes","Cutaneous T-cell lymphoma, unspecified",9
C84Z,2,C84Z2,"Other mature T/NK-cell lymphomas, intrathoracic lymph nodes","Other mature T/NK-cell lymphomas, intrathoracic lymph nodes",Other mature T/NK-cell lymphomas,9
C849,2,C8492,"Mature T/NK-cell lymphomas, unsp, intrathoracic lymph nodes","Mature T/NK-cell lymphomas, unspecified, intrathoracic lymph nodes","Mature T/NK-cell lymphomas, unspecified",9
C851,2,C8512,"Unspecified B-cell lymphoma, intrathoracic lymph nodes","Unspecified B-cell lymphoma, intrathoracic lymph nodes",Unspecified B-cell lymphoma,9
C852,2,C8522,"Mediastnl (thymic) large B-cell lymphoma, intrathorac nodes","Mediastinal (thymic) large B-cell lymphoma, intrathoracic lymph nodes",Mediastinal (thymic) large B-cell lymphoma,9
C858,2,C8582,"Oth types of non-Hodgkin lymphoma, intrathoracic lymph nodes","Other specified types of non-Hodgkin lymphoma, intrathoracic lymph nodes",Other specified types of non-Hodgkin lymphoma,9
C859,2,C8592,"Non-Hodgkin lymphoma, unspecified, intrathoracic lymph nodes","Non-Hodgkin lymphoma, unspecified, intrathoracic lymph nodes","Non-Hodgkin lymphoma, unspecified",9
C86,2,C862,Enteropathy-type (intestinal) T-cell lymphoma,Enteropathy-type (intestinal) T-cell lymphoma,Other specified types of T/NK-cell lymphoma,9
C88,2,C882,Heavy chain disease,Heavy chain disease,Malignant immunoproliferative diseases and certain other B-cell lymphomas,9
C900,2,C9002,Multiple myeloma in relapse,Multiple myeloma in relapse,Multiple myeloma,9
C901,2,C9012,Plasma cell leukemia in relapse,Plasma cell leukemia in relapse,Plasma cell leukemia,9
C902,2,C9022,Extramedullary plasmacytoma in relapse,Extramedullary plasmacytoma in relapse,Extramedullary plasmacytoma,9
C903,2,C9032,Solitary plasmacytoma in relapse,Solitary plasmacytoma in relapse,Solitary plasmacytoma,9
C910,2,C9102,"Acute lymphoblastic leukemia, in relapse","Acute lymphoblastic leukemia, in relapse",Acute lymphoblastic leukemia [ALL],9
C911,2,C9112,Chronic lymphocytic leukemia of B-cell type in relapse,Chronic lymphocytic leukemia of B-cell type in relapse,Chronic lymphocytic leukemia of B-cell type,9
C913,2,C9132,"Prolymphocytic leukemia of B-cell type, in relapse","Prolymphocytic leukemia of B-cell type, in relapse",Prolymphocytic leukemia of B-cell type,9
C914,2,C9142,"Hairy cell leukemia, in relapse","Hairy cell leukemia, in relapse",Hairy cell leukemia,9
C915,2,C9152,"Adult T-cell lymphoma/leukemia (HTLV-1-assoc), in relapse","Adult T-cell lymphoma/leukemia (HTLV-1-associated), in relapse",Adult T-cell lymphoma/leukemia (HTLV-1-associated),9
C916,2,C9162,"Prolymphocytic leukemia of T-cell type, in relapse","Prolymphocytic leukemia of T-cell type, in relapse",Prolymphocytic leukemia of T-cell type,9
C91A,2,C91A2,"Mature B-cell leukemia Burkitt-type, in relapse","Mature B-cell leukemia Burkitt-type, in relapse",Mature B-cell leukemia Burkitt-type,9
C91Z,2,C91Z2,"Other lymphoid leukemia, in relapse","Other lymphoid leukemia, in relapse",Other lymphoid leukemia,9
C919,2,C9192,"Lymphoid leukemia, unspecified, in relapse","Lymphoid leukemia, unspecified, in relapse","Lymphoid leukemia, unspecified",9
C920,2,C9202,"Acute myeloblastic leukemia, in relapse","Acute myeloblastic leukemia, in relapse",Acute myeloblastic leukemia,9
C921,2,C9212,"Chronic myeloid leukemia, BCR/ABL-positive, in relapse","Chronic myeloid leukemia, BCR/ABL-positive, in relapse","Chronic myeloid leukemia, BCR/ABL-positive",9
C922,2,C9222,"Atypical chronic myeloid leukemia, BCR/ABL-neg, in relapse","Atypical chronic myeloid leukemia, BCR/ABL-negative, in relapse","Atypical chronic myeloid leukemia, BCR/ABL-negative",9
C923,2,C9232,"Myeloid sarcoma, in relapse","Myeloid sarcoma, in relapse",Myeloid sarcoma,9
C924,2,C9242,"Acute promyelocytic leukemia, in relapse","Acute promyelocytic leukemia, in relapse",Acute promyelocytic leukemia,9
C925,2,C9252,"Acute myelomonocytic leukemia, in relapse","Acute myelomonocytic leukemia, in relapse",Acute myelomonocytic leukemia,9
C926,2,C9262,Acute myeloid leukemia with 11q23-abnormality in relapse,Acute myeloid leukemia with 11q23-abnormality in relapse,Acute myeloid leukemia with 11q23-abnormality,9
C92A,2,C92A2,"Acute myeloid leukemia w multilineage dysplasia, in relapse","Acute myeloid leukemia with multilineage dysplasia, in relapse",Acute myeloid leukemia with multilineage dysplasia,9
C92Z,2,C92Z2,"Other myeloid leukemia, in relapse","Other myeloid leukemia, in relapse",Other myeloid leukemia,9
C929,2,C9292,"Myeloid leukemia, unspecified in relapse","Myeloid leukemia, unspecified in relapse","Myeloid leukemia, unspecified",9
C930,2,C9302,"Acute monoblastic/monocytic leukemia, in relapse","Acute monoblastic/monocytic leukemia, in relapse",Acute monoblastic/monocytic leukemia,9
C931,2,C9312,"Chronic myelomonocytic leukemia, in relapse","Chronic myelomonocytic leukemia, in relapse",Chronic myelomonocytic leukemia,9
C933,2,C9332,"Juvenile myelomonocytic leukemia, in relapse","Juvenile myelomonocytic leukemia, in relapse",Juvenile myelomonocytic leukemia,9
C93Z,2,C93Z2,"Other monocytic leukemia, in relapse","Other monocytic leukemia, in relapse",Other monocytic leukemia,9
C939,2,C9392,"Monocytic leukemia, unspecified in relapse","Monocytic leukemia, unspecified in relapse","Monocytic leukemia, unspecified",9
C940,2,C9402,"Acute erythroid leukemia, in relapse","Acute erythroid leukemia, in relapse",Acute erythroid leukemia,9
C942,2,C9422,"Acute megakaryoblastic leukemia, in relapse","Acute megakaryoblastic leukemia, in relapse",Acute megakaryoblastic leukemia,9
C943,2,C9432,"Mast cell leukemia, in relapse","Mast cell leukemia, in relapse",Mast cell leukemia,9
C944,2,C9442,"Acute panmyelosis with myelofibrosis, in relapse","Acute panmyelosis with myelofibrosis, in relapse",Acute panmyelosis with myelofibrosis,9
C948,2,C9482,"Other specified leukemias, in relapse","Other specified leukemias, in relapse",Other specified leukemias,9
C950,2,C9502,"Acute leukemia of unspecified cell type, in relapse","Acute leukemia of unspecified cell type, in relapse",Acute leukemia of unspecified cell type,9
C951,2,C9512,"Chronic leukemia of unspecified cell type, in relapse","Chronic leukemia of unspecified cell type, in relapse",Chronic leukemia of unspecified cell type,9
C959,2,C9592,"Leukemia, unspecified, in relapse","Leukemia, unspecified, in relapse","Leukemia, unspecified",9
C962,2,C9622,Mast cell sarcoma,Mast cell sarcoma,Malignant mast cell neoplasm,9
D000,2,D0002,Carcinoma in situ of buccal mucosa,Carcinoma in situ of buccal mucosa,"Carcinoma in situ of lip, oral cavity and pharynx",9
D01,2,D012,Carcinoma in situ of rectum,Carcinoma in situ of rectum,Carcinoma in situ of other and unspecified digestive organs,9
D022,2,D0222,Carcinoma in situ of left bronchus and lung,Carcinoma in situ of left bronchus and lung,Carcinoma in situ of bronchus and lung,9
D031,2,D0312,"Melanoma in situ of left eyelid, including canthus","Melanoma in situ of left eyelid, including canthus","Melanoma in situ of eyelid, including canthus",9
D032,2,D0322,Melanoma in situ of left ear and external auricular canal,Melanoma in situ of left ear and external auricular canal,Melanoma in situ of ear and external auricular canal,9
D035,2,D0352,Melanoma in situ of breast (skin) (soft tissue),Melanoma in situ of breast (skin) (soft tissue),Melanoma in situ of trunk,9
D036,2,D0362,"Melanoma in situ of left upper limb, including shoulder","Melanoma in situ of left upper limb, including shoulder","Melanoma in situ of upper limb, including shoulder",9
D037,2,D0372,"Melanoma in situ of left lower limb, including hip","Melanoma in situ of left lower limb, including hip","Melanoma in situ of lower limb, including hip",9
D041,2,D0412,"Carcinoma in situ of skin of left eyelid, including canthus","Carcinoma in situ of skin of left eyelid, including canthus","Carcinoma in situ of skin of eyelid, including canthus",9
D042,2,D0422,Ca in situ skin of left ear and external auricular canal,Carcinoma in situ of skin of left ear and external auricular canal,Carcinoma in situ of skin of ear and external auricular canal,9
D046,2,D0462,"Ca in situ skin of left upper limb, including shoulder","Carcinoma in situ of skin of left upper limb, including shoulder","Carcinoma in situ of skin of upper limb, including shoulder",9
D047,2,D0472,"Carcinoma in situ of skin of left lower limb, including hip","Carcinoma in situ of skin of left lower limb, including hip","Carcinoma in situ of skin of lower limb, including hip",9
D050,2,D0502,Lobular carcinoma in situ of left breast,Lobular carcinoma in situ of left breast,Lobular carcinoma in situ of breast,9
D051,2,D0512,Intraductal carcinoma in situ of left breast,Intraductal carcinoma in situ of left breast,Intraductal carcinoma in situ of breast,9
D058,2,D0582,Other specified type of carcinoma in situ of left breast,Other specified type of carcinoma in situ of left breast,Other specified type of carcinoma in situ of breast,9
D059,2,D0592,Unspecified type of carcinoma in situ of left breast,Unspecified type of carcinoma in situ of left breast,Unspecified type of carcinoma in situ of breast,9
D07,2,D072,Carcinoma in situ of vagina,Carcinoma in situ of vagina,Carcinoma in situ of other and unspecified genital organs,9
D092,2,D0922,Carcinoma in situ of left eye,Carcinoma in situ of left eye,Carcinoma in situ of eye,9
D10,2,D102,Benign neoplasm of floor of mouth,Benign neoplasm of floor of mouth,Benign neoplasm of mouth and pharynx,9
D12,2,D122,Benign neoplasm of ascending colon,Benign neoplasm of ascending colon,"Benign neoplasm of colon, rectum, anus and anal canal",9
D13,2,D132,Benign neoplasm of duodenum,Benign neoplasm of duodenum,Benign neoplasm of other and ill-defined parts of digestive system,9
D14,2,D142,Benign neoplasm of trachea,Benign neoplasm of trachea,Benign neoplasm of middle ear and respiratory system,9
D143,2,D1432,Benign neoplasm of left bronchus and lung,Benign neoplasm of left bronchus and lung,Benign neoplasm of bronchus and lung,9
D15,2,D152,Benign neoplasm of mediastinum,Benign neoplasm of mediastinum,Benign neoplasm of other and unspecified intrathoracic organs,9
D160,2,D1602,Benign neoplasm of scapula and long bones of left upper limb,Benign neoplasm of scapula and long bones of left upper limb,Benign neoplasm of scapula and long bones of upper limb,9
D161,2,D1612,Benign neoplasm of short bones of left upper limb,Benign neoplasm of short bones of left upper limb,Benign neoplasm of short bones of upper limb,9
D162,2,D1622,Benign neoplasm of long bones of left lower limb,Benign neoplasm of long bones of left lower limb,Benign neoplasm of long bones of lower limb,9
E79,2,E792,Myoadenylate deaminase deficiency,Myoadenylate deaminase deficiency,Disorders of purine and pyrimidine metabolism,9
D163,2,D1632,Benign neoplasm of short bones of left lower limb,Benign neoplasm of short bones of left lower limb,Benign neoplasm of short bones of lower limb,9
D172,2,D1722,"Benign lipomatous neoplasm of skin, subcu of left arm",Benign lipomatous neoplasm of skin and subcutaneous tissue of left arm,Benign lipomatous neoplasm of skin and subcutaneous tissue of limb,9
D177,2,D1772,Benign lipomatous neoplasm of other genitourinary organ,Benign lipomatous neoplasm of other genitourinary organ,Benign lipomatous neoplasm of other sites,9
D180,2,D1802,Hemangioma of intracranial structures,Hemangioma of intracranial structures,Hemangioma,9
D211,2,D2112,"Ben neoplm of connctv/soft tiss of left upr limb, inc shldr","Benign neoplasm of connective and other soft tissue of left upper limb, including shoulder","Benign neoplasm of connective and other soft tissue of upper limb, including shoulder",9
D212,2,D2122,"Ben neoplm of connctv/soft tiss of left lower limb, inc hip","Benign neoplasm of connective and other soft tissue of left lower limb, including hip","Benign neoplasm of connective and other soft tissue of lower limb, including hip",9
D221,2,D2212,"Melanocytic nevi of left eyelid, including canthus","Melanocytic nevi of left eyelid, including canthus","Melanocytic nevi of eyelid, including canthus",9
D222,2,D2222,Melanocytic nevi of left ear and external auricular canal,Melanocytic nevi of left ear and external auricular canal,Melanocytic nevi of ear and external auricular canal,9
D226,2,D2262,"Melanocytic nevi of left upper limb, including shoulder","Melanocytic nevi of left upper limb, including shoulder","Melanocytic nevi of upper limb, including shoulder",9
D227,2,D2272,"Melanocytic nevi of left lower limb, including hip","Melanocytic nevi of left lower limb, including hip","Melanocytic nevi of lower limb, including hip",9
D231,2,D2312,"Oth benign neoplasm skin/ left eyelid, including canthus","Other benign neoplasm of skin of left eyelid, including canthus","Other benign neoplasm of skin of eyelid, including canthus",9
D232,2,D2322,Oth benign neoplasm skin/ left ear and external auric canal,Other benign neoplasm of skin of left ear and external auricular canal,Other benign neoplasm of skin of ear and external auricular canal,9
D236,2,D2362,"Oth benign neoplasm skin/ left upper limb, inc shoulder","Other benign neoplasm of skin of left upper limb, including shoulder","Other benign neoplasm of skin of upper limb, including shoulder",9
D237,2,D2372,"Oth benign neoplasm skin/ left lower limb, including hip","Other benign neoplasm of skin of left lower limb, including hip","Other benign neoplasm of skin of lower limb, including hip",9
D24,2,D242,Benign neoplasm of left breast,Benign neoplasm of left breast,Benign neoplasm of breast,9
D25,2,D252,Subserosal leiomyoma of uterus,Subserosal leiomyoma of uterus,Leiomyoma of uterus,9
D28,2,D282,Benign neoplasm of uterine tubes and ligaments,Benign neoplasm of uterine tubes and ligaments,Benign neoplasm of other and unspecified female genital organs,9
D292,2,D2922,Benign neoplasm of left testis,Benign neoplasm of left testis,Benign neoplasm of testis,9
D293,2,D2932,Benign neoplasm of left epididymis,Benign neoplasm of left epididymis,Benign neoplasm of epididymis,9
D300,2,D3002,Benign neoplasm of left kidney,Benign neoplasm of left kidney,Benign neoplasm of kidney,9
D301,2,D3012,Benign neoplasm of left renal pelvis,Benign neoplasm of left renal pelvis,Benign neoplasm of renal pelvis,9
D302,2,D3022,Benign neoplasm of left ureter,Benign neoplasm of left ureter,Benign neoplasm of ureter,9
D310,2,D3102,Benign neoplasm of left conjunctiva,Benign neoplasm of left conjunctiva,Benign neoplasm of conjunctiva,9
D311,2,D3112,Benign neoplasm of left cornea,Benign neoplasm of left cornea,Benign neoplasm of cornea,9
D312,2,D3122,Benign neoplasm of left retina,Benign neoplasm of left retina,Benign neoplasm of retina,9
D313,2,D3132,Benign neoplasm of left choroid,Benign neoplasm of left choroid,Benign neoplasm of choroid,9
D314,2,D3142,Benign neoplasm of left ciliary body,Benign neoplasm of left ciliary body,Benign neoplasm of ciliary body,9
D315,2,D3152,Benign neoplasm of left lacrimal gland and duct,Benign neoplasm of left lacrimal gland and duct,Benign neoplasm of lacrimal gland and duct,9
D316,2,D3162,Benign neoplasm of unspecified site of left orbit,Benign neoplasm of unspecified site of left orbit,Benign neoplasm of unspecified site of orbit,9
D319,2,D3192,Benign neoplasm of unspecified part of left eye,Benign neoplasm of unspecified part of left eye,Benign neoplasm of unspecified part of eye,9
D33,2,D332,"Benign neoplasm of brain, unspecified","Benign neoplasm of brain, unspecified",Benign neoplasm of brain and other parts of central nervous system,9
D350,2,D3502,Benign neoplasm of left adrenal gland,Benign neoplasm of left adrenal gland,Benign neoplasm of adrenal gland,9
D361,2,D3612,"Ben neoplm of prph nrv & autonm nrv sys, upr lmb, inc shldr","Benign neoplasm of peripheral nerves and autonomic nervous system, upper limb, including shoulder",Benign neoplasm of peripheral nerves and autonomic nervous system,9
D3A01,2,D3A012,Benign carcinoid tumor of the ileum,Benign carcinoid tumor of the ileum,Benign carcinoid tumors of the small intestine,9
D3A02,2,D3A022,Benign carcinoid tumor of the ascending colon,Benign carcinoid tumor of the ascending colon,"Benign carcinoid tumors of the appendix, large intestine, and rectum",9
D3A09,2,D3A092,Benign carcinoid tumor of the stomach,Benign carcinoid tumor of the stomach,Benign carcinoid tumors of other sites,9
D370,2,D3702,Neoplasm of uncertain behavior of tongue,Neoplasm of uncertain behavior of tongue,"Neoplasm of uncertain behavior of lip, oral cavity and pharynx",9
D3703,2,D37032,Neoplasm of uncrt behav of the submandibular salivary gland,Neoplasm of uncertain behavior of the submandibular salivary glands,Neoplasm of uncertain behavior of the major salivary glands,9
D38,2,D382,Neoplasm of uncertain behavior of pleura,Neoplasm of uncertain behavior of pleura,Neoplasm of uncertain behavior of middle ear and respiratory and intrathoracic organs,9
D391,2,D3912,Neoplasm of uncertain behavior of left ovary,Neoplasm of uncertain behavior of left ovary,Neoplasm of uncertain behavior of ovary,9
D401,2,D4012,Neoplasm of uncertain behavior of left testis,Neoplasm of uncertain behavior of left testis,Neoplasm of uncertain behavior of testis,9
D410,2,D4102,Neoplasm of uncertain behavior of left kidney,Neoplasm of uncertain behavior of left kidney,Neoplasm of uncertain behavior of kidney,9
D411,2,D4112,Neoplasm of uncertain behavior of left renal pelvis,Neoplasm of uncertain behavior of left renal pelvis,Neoplasm of uncertain behavior of renal pelvis,9
D412,2,D4122,Neoplasm of uncertain behavior of left ureter,Neoplasm of uncertain behavior of left ureter,Neoplasm of uncertain behavior of ureter,9
D43,2,D432,"Neoplasm of uncertain behavior of brain, unspecified","Neoplasm of uncertain behavior of brain, unspecified",Neoplasm of uncertain behavior of brain and central nervous system,9
D441,2,D4412,Neoplasm of uncertain behavior of left adrenal gland,Neoplasm of uncertain behavior of left adrenal gland,Neoplasm of uncertain behavior of adrenal gland,9
D462,2,D4622,Refractory anemia with excess of blasts 2,Refractory anemia with excess of blasts 2,Refractory anemia with excess of blasts [RAEB],9
D470,2,D4702,Systemic mastocytosis,Systemic mastocytosis,Mast cell neoplasms of uncertain behavior,9
D47Z,2,D47Z2,Castleman disease,Castleman disease,"Other specified neoplasms of uncertain behavior of lymphoid, hematopoietic and related tissue",9
D48,2,D482,Neoplm of uncrt behav of prph nerves and autonm nervous sys,Neoplasm of uncertain behavior of peripheral nerves and autonomic nervous system,Neoplasm of uncertain behavior of other and unspecified sites,9
D486,2,D4862,Neoplasm of uncertain behavior of left breast,Neoplasm of uncertain behavior of left breast,Neoplasm of uncertain behavior of breast,9
D49,2,D492,"Neoplasm of unsp behavior of bone, soft tissue, and skin","Neoplasm of unspecified behavior of bone, soft tissue, and skin",Neoplasms of unspecified behavior,9
D4951,2,D49512,Neoplasm of unspecified behavior of left kidney,Neoplasm of unspecified behavior of left kidney,Neoplasm of unspecified behavior of kidney,9
D51,2,D512,Transcobalamin II deficiency,Transcobalamin II deficiency,Vitamin B12 deficiency anemia,9
D53,2,D532,Scorbutic anemia,Scorbutic anemia,Other nutritional anemias,9
D55,2,D552,Anemia due to disorders of glycolytic enzymes,Anemia due to disorders of glycolytic enzymes,Anemia due to enzyme disorders,9
D56,2,D562,Delta-beta thalassemia,Delta-beta thalassemia,Thalassemia,9
D570,2,D5702,Hb-SS disease with splenic sequestration,Hb-SS disease with splenic sequestration,Hb-SS disease with crisis,9
D5721,2,D57212,Sickle-cell/Hb-C disease with splenic sequestration,Sickle-cell/Hb-C disease with splenic sequestration,Sickle-cell/Hb-C disease with crisis,9
D5741,2,D57412,Sickle-cell thalassemia with splenic sequestration,Sickle-cell thalassemia with splenic sequestration,Sickle-cell thalassemia with crisis,9
D5781,2,D57812,Other sickle-cell disorders with splenic sequestration,Other sickle-cell disorders with splenic sequestration,Other sickle-cell disorders with crisis,9
D58,2,D582,Other hemoglobinopathies,Other hemoglobinopathies,Other hereditary hemolytic anemias,9
D59,2,D592,Drug-induced nonautoimmune hemolytic anemia,Drug-induced nonautoimmune hemolytic anemia,Acquired hemolytic anemia,9
D64,2,D642,Secondary sideroblastic anemia due to drugs and toxins,Secondary sideroblastic anemia due to drugs and toxins,Other anemias,9
D68,2,D682,Hereditary deficiency of other clotting factors,Hereditary deficiency of other clotting factors,Other coagulation defects,9
D6831,2,D68312,Antiphospholipid antibody with hemorrhagic disorder,Antiphospholipid antibody with hemorrhagic disorder,"Hemorrhagic disorder due to intrinsic circulating anticoagulants, antibodies, or inhibitors",9
D685,2,D6852,Prothrombin gene mutation,Prothrombin gene mutation,Primary thrombophilia,9
D686,2,D6862,Lupus anticoagulant syndrome,Lupus anticoagulant syndrome,Other thrombophilia,9
D69,2,D692,Other nonthrombocytopenic purpura,Other nonthrombocytopenic purpura,Purpura and other hemorrhagic conditions,9
D694,2,D6942,Congenital and hereditary thrombocytopenia purpura,Congenital and hereditary thrombocytopenia purpura,Other primary thrombocytopenia,9
D70,2,D702,Other drug-induced agranulocytosis,Other drug-induced agranulocytosis,Neutropenia,9
D7282,2,D72822,Plasmacytosis,Plasmacytosis,Elevated white blood cell count,9
D73,2,D732,Chronic congestive splenomegaly,Chronic congestive splenomegaly,Diseases of spleen,9
D758,2,D7582,Heparin induced thrombocytopenia (HIT),Heparin induced thrombocytopenia (HIT),Other specified diseases of blood and blood-forming organs,9
D76,2,D762,"Hemophagocytic syndrome, infection-associated","Hemophagocytic syndrome, infection-associated",Other specified diseases with participation of lymphoreticular and reticulohistiocytic tissue,9
D780,2,D7802,Intraop hemor/hemtom of the spleen comp oth procedure,Intraoperative hemorrhage and hematoma of the spleen complicating other procedure,Intraoperative hemorrhage and hematoma of the spleen complicating a procedure,9
D781,2,D7812,Accidental pnctr & lac of the spleen during oth procedure,Accidental puncture and laceration of the spleen during other procedure,Accidental puncture and laceration of the spleen during a procedure,9
D782,2,D7822,Postproc hemorrhage of the spleen following other procedure,Postprocedural hemorrhage of the spleen following other procedure,Postprocedural hemorrhage of the spleen following a procedure,9
D783,2,D7832,Postproc hematoma of the spleen following other procedure,Postprocedural hematoma of the spleen following other procedure,Postprocedural hematoma and seroma of the spleen following a procedure,9
D80,2,D802,Selective deficiency of immunoglobulin A [IgA],Selective deficiency of immunoglobulin A [IgA],Immunodeficiency with predominantly antibody defects,9
D81,2,D812,Severe combined immunodef w low or normal B-cell numbers,Severe combined immunodeficiency [SCID] with low or normal B-cell numbers,Combined immunodeficiencies,9
D82,2,D822,Immunodeficiency with short-limbed stature,Immunodeficiency with short-limbed stature,Immunodeficiency associated with other major defects,9
D83,2,D832,Common variable immunodef w autoantibodies to B- or T-cells,Common variable immunodeficiency with autoantibodies to B- or T-cells,Common variable immunodeficiency,9
D86,2,D862,Sarcoidosis of lung with sarcoidosis of lymph nodes,Sarcoidosis of lung with sarcoidosis of lymph nodes,Sarcoidosis,9
D868,2,D8682,Multiple cranial nerve palsies in sarcoidosis,Multiple cranial nerve palsies in sarcoidosis,Sarcoidosis of other sites,9
D89,2,D892,"Hypergammaglobulinemia, unspecified","Hypergammaglobulinemia, unspecified","Other disorders involving the immune mechanism, not elsewhere classified",9
D894,2,D8942,Idiopathic mast cell activation syndrome,Idiopathic mast cell activation syndrome,Mast cell activation syndrome and related disorders,9
D8981,2,D89812,Acute on chronic graft-versus-host disease,Acute on chronic graft-versus-host disease,Graft-versus-host disease,9
E00,2,E002,"Congenital iodine-deficiency syndrome, mixed type","Congenital iodine-deficiency syndrome, mixed type",Congenital iodine-deficiency syndrome,9
E01,2,E012,"Iodine-deficiency related (endemic) goiter, unspecified","Iodine-deficiency related (endemic) goiter, unspecified",Iodine-deficiency related thyroid disorders and allied conditions,9
E03,2,E032,Hypothyroidism due to meds and oth exogenous substances,Hypothyroidism due to medicaments and other exogenous substances,Other hypothyroidism,9
E04,2,E042,Nontoxic multinodular goiter,Nontoxic multinodular goiter,Other nontoxic goiter,9
E06,2,E062,Chronic thyroiditis with transient thyrotoxicosis,Chronic thyroiditis with transient thyrotoxicosis,Thyroiditis,9
E082,2,E0822,Diabetes due to undrl cond w diabetic chronic kidney disease,Diabetes mellitus due to underlying condition with diabetic chronic kidney disease,Diabetes mellitus due to underlying condition with kidney complications,9
E08321,2,E083212,"Diabetes with mild nonp rtnop with macular edema, left eye","Diabetes mellitus due to underlying condition with mild nonproliferative diabetic retinopathy with macular edema, left eye",Diabetes mellitus due to underlying condition with mild nonproliferative diabetic retinopathy with macular edema,9
E08329,2,E083292,"Diab with mild nonp rtnop without macular edema, left eye","Diabetes mellitus due to underlying condition with mild nonproliferative diabetic retinopathy without macular edema, left eye",Diabetes mellitus due to underlying condition with mild nonproliferative diabetic retinopathy without macular edema,9
E08331,2,E083312,"Diab with moderate nonp rtnop with macular edema, left eye","Diabetes mellitus due to underlying condition with moderate nonproliferative diabetic retinopathy with macular edema, left eye",Diabetes mellitus due to underlying condition with moderate nonproliferative diabetic retinopathy with macular edema,9
E08339,2,E083392,"Diab with moderate nonp rtnop without macular edema, l eye","Diabetes mellitus due to underlying condition with moderate nonproliferative diabetic retinopathy without macular edema, left eye",Diabetes mellitus due to underlying condition with moderate nonproliferative diabetic retinopathy without macular edema,9
E08341,2,E083412,"Diabetes with severe nonp rtnop with macular edema, left eye","Diabetes mellitus due to underlying condition with severe nonproliferative diabetic retinopathy with macular edema, left eye",Diabetes mellitus due to underlying condition with severe nonproliferative diabetic retinopathy with macular edema,9
E08349,2,E083492,"Diab with severe nonp rtnop without macular edema, left eye","Diabetes mellitus due to underlying condition with severe nonproliferative diabetic retinopathy without macular edema, left eye",Diabetes mellitus due to underlying condition with severe nonproliferative diabetic retinopathy without macular edema,9
E08351,2,E083512,"Diab with prolif diabetic rtnop with macular edema, left eye","Diabetes mellitus due to underlying condition with proliferative diabetic retinopathy with macular edema, left eye",Diabetes mellitus due to underlying condition with proliferative diabetic retinopathy with macular edema,9
E08352,2,E083522,"Diab with prolif diab rtnop with trctn dtch macula, left eye","Diabetes mellitus due to underlying condition with proliferative diabetic retinopathy with traction retinal detachment involving the macula, left eye",Diabetes mellitus due to underlying condition with proliferative diabetic retinopathy with traction retinal detachment involving the macula,9
E08353,2,E083532,"Diab with prolif diab rtnop with trctn dtch n-mcla, left eye","Diabetes mellitus due to underlying condition with proliferative diabetic retinopathy with traction retinal detachment not involving the macula, left eye",Diabetes mellitus due to underlying condition with proliferative diabetic retinopathy with traction retinal detachment not involving the macula,9
E08354,2,E083542,"Diab with prolif diabetic rtnop with comb detach, left eye","Diabetes mellitus due to underlying condition with proliferative diabetic retinopathy with combined traction retinal detachment and rhegmatogenous retinal detachment, left eye",Diabetes mellitus due to underlying condition with proliferative diabetic retinopathy with combined traction retinal detachment and rhegmatogenous retinal detachment,9
E08355,2,E083552,"Diabetes with stable prolif diabetic retinopathy, left eye","Diabetes mellitus due to underlying condition with stable proliferative diabetic retinopathy, left eye",Diabetes mellitus due to underlying condition with stable proliferative diabetic retinopathy,9
E08359,2,E083592,"Diab with prolif diab rtnop without macular edema, left eye","Diabetes mellitus due to underlying condition with proliferative diabetic retinopathy without macular edema, left eye",Diabetes mellitus due to underlying condition with proliferative diabetic retinopathy without macular edema,9
E084,2,E0842,Diabetes due to underlying condition w diabetic polyneurop,Diabetes mellitus due to underlying condition with diabetic polyneuropathy,Diabetes mellitus due to underlying condition with neurological complications,9
E085,2,E0852,Diab due to undrl cond w diabetic prph angiopath w gangrene,Diabetes mellitus due to underlying condition with diabetic peripheral angiopathy with gangrene,Diabetes mellitus due to underlying condition with circulatory complications,9
E0862,2,E08622,Diabetes due to underlying condition w oth skin ulcer,Diabetes mellitus due to underlying condition with other skin ulcer,Diabetes mellitus due to underlying condition with skin complications,9
E092,2,E0922,Drug/chem diabetes w diabetic chronic kidney disease,Drug or chemical induced diabetes mellitus with diabetic chronic kidney disease,Drug or chemical induced diabetes mellitus with kidney complications,9
E09321,2,E093212,"Drug/chem diab with mild nonp rtnop with mclr edema, l eye","Drug or chemical induced diabetes mellitus with mild nonproliferative diabetic retinopathy with macular edema, left eye",Drug or chemical induced diabetes mellitus with mild nonproliferative diabetic retinopathy with macular edema,9
E09329,2,E093292,"Drug/chem diab with mild nonp rtnop w/o mclr edema, l eye","Drug or chemical induced diabetes mellitus with mild nonproliferative diabetic retinopathy without macular edema, left eye",Drug or chemical induced diabetes mellitus with mild nonproliferative diabetic retinopathy without macular edema,9
E09331,2,E093312,"Drug/chem diab with mod nonp rtnop with macular edema, l eye","Drug or chemical induced diabetes mellitus with moderate nonproliferative diabetic retinopathy with macular edema, left eye",Drug or chemical induced diabetes mellitus with moderate nonproliferative diabetic retinopathy with macular edema,9
E09339,2,E093392,"Drug/chem diab with mod nonp rtnop without mclr edema, l eye","Drug or chemical induced diabetes mellitus with moderate nonproliferative diabetic retinopathy without macular edema, left eye",Drug or chemical induced diabetes mellitus with moderate nonproliferative diabetic retinopathy without macular edema,9
E09341,2,E093412,"Drug/chem diab with severe nonp rtnop with mclr edema, l eye","Drug or chemical induced diabetes mellitus with severe nonproliferative diabetic retinopathy with macular edema, left eye",Drug or chemical induced diabetes mellitus with severe nonproliferative diabetic retinopathy with macular edema,9
E09349,2,E093492,"Drug/chem diab with severe nonp rtnop w/o mclr edema, l eye","Drug or chemical induced diabetes mellitus with severe nonproliferative diabetic retinopathy without macular edema, left eye",Drug or chemical induced diabetes mellitus with severe nonproliferative diabetic retinopathy without macular edema,9
E09351,2,E093512,"Drug/chem diab with prolif diab rtnop with mclr edema, l eye","Drug or chemical induced diabetes mellitus with proliferative diabetic retinopathy with macular edema, left eye",Drug or chemical induced diabetes mellitus with proliferative diabetic retinopathy with macular edema,9
E09352,2,E093522,"Drug/chem diab w prolif diab rtnop w trctn dtch macula,l eye","Drug or chemical induced diabetes mellitus with proliferative diabetic retinopathy with traction retinal detachment involving the macula, left eye",Drug or chemical induced diabetes mellitus with proliferative diabetic retinopathy with traction retinal detachment involving the macula,9
E09353,2,E093532,"Drug/chem diab w prolif diab rtnop w trctn dtch n-mcla,l eye","Drug or chemical induced diabetes mellitus with proliferative diabetic retinopathy with traction retinal detachment not involving the macula, left eye",Drug or chemical induced diabetes mellitus with proliferative diabetic retinopathy with traction retinal detachment not involving the macula,9
E09354,2,E093542,"Drug/chem diab w prolif diab rtnop with comb detach, l eye","Drug or chemical induced diabetes mellitus with proliferative diabetic retinopathy with combined traction retinal detachment and rhegmatogenous retinal detachment, left eye",Drug or chemical induced diabetes mellitus with proliferative diabetic retinopathy with combined traction retinal detachment and rhegmatogenous retinal detachment,9
E09355,2,E093552,"Drug/chem diab with stable prolif diabetic rtnop, left eye","Drug or chemical induced diabetes mellitus with stable proliferative diabetic retinopathy, left eye",Drug or chemical induced diabetes mellitus with stable proliferative diabetic retinopathy,9
E09359,2,E093592,"Drug/chem diab with prolif diab rtnop w/o mclr edema, l eye","Drug or chemical induced diabetes mellitus with proliferative diabetic retinopathy without macular edema, left eye",Drug or chemical induced diabetes mellitus with proliferative diabetic retinopathy without macular edema,9
E094,2,E0942,Drug/chem diabetes w neurological comp w diabetic polyneurop,Drug or chemical induced diabetes mellitus with neurological complications with diabetic polyneuropathy,Drug or chemical induced diabetes mellitus with neurological complications,9
E095,2,E0952,Drug/chem diabetes w diabetic prph angiopath w gangrene,Drug or chemical induced diabetes mellitus with diabetic peripheral angiopathy with gangrene,Drug or chemical induced diabetes mellitus with circulatory complications,9
E0962,2,E09622,Drug or chemical induced diabetes mellitus w oth skin ulcer,Drug or chemical induced diabetes mellitus with other skin ulcer,Drug or chemical induced diabetes mellitus with skin complications,9
E102,2,E1022,Type 1 diabetes mellitus w diabetic chronic kidney disease,Type 1 diabetes mellitus with diabetic chronic kidney disease,Type 1 diabetes mellitus with kidney complications,9
E10321,2,E103212,"Type 1 diab with mild nonp rtnop with macular edema, l eye","Type 1 diabetes mellitus with mild nonproliferative diabetic retinopathy with macular edema, left eye",Type 1 diabetes mellitus with mild nonproliferative diabetic retinopathy with macular edema,9
E10329,2,E103292,"Type 1 diab with mild nonp rtnop without mclr edema, l eye","Type 1 diabetes mellitus with mild nonproliferative diabetic retinopathy without macular edema, left eye",Type 1 diabetes mellitus with mild nonproliferative diabetic retinopathy without macular edema,9
E10331,2,E103312,"Type 1 diab with mod nonp rtnop with macular edema, l eye","Type 1 diabetes mellitus with moderate nonproliferative diabetic retinopathy with macular edema, left eye",Type 1 diabetes mellitus with moderate nonproliferative diabetic retinopathy with macular edema,9
E10339,2,E103392,"Type 1 diab with mod nonp rtnop without macular edema, l eye","Type 1 diabetes mellitus with moderate nonproliferative diabetic retinopathy without macular edema, left eye",Type 1 diabetes mellitus with moderate nonproliferative diabetic retinopathy without macular edema,9
E10341,2,E103412,"Type 1 diab with severe nonp rtnop with macular edema, l eye","Type 1 diabetes mellitus with severe nonproliferative diabetic retinopathy with macular edema, left eye",Type 1 diabetes mellitus with severe nonproliferative diabetic retinopathy with macular edema,9
E10349,2,E103492,"Type 1 diab with severe nonp rtnop without mclr edema, l eye","Type 1 diabetes mellitus with severe nonproliferative diabetic retinopathy without macular edema, left eye",Type 1 diabetes mellitus with severe nonproliferative diabetic retinopathy without macular edema,9
E10351,2,E103512,"Type 1 diab with prolif diab rtnop with macular edema, l eye","Type 1 diabetes mellitus with proliferative diabetic retinopathy with macular edema, left eye",Type 1 diabetes mellitus with proliferative diabetic retinopathy with macular edema,9
E10352,2,E103522,"Type 1 diab w prolif diab rtnop w trctn dtch macula, l eye","Type 1 diabetes mellitus with proliferative diabetic retinopathy with traction retinal detachment involving the macula, left eye",Type 1 diabetes mellitus with proliferative diabetic retinopathy with traction retinal detachment involving the macula,9
E10353,2,E103532,"Type 1 diab w prolif diab rtnop w trctn dtch n-mcla, l eye","Type 1 diabetes mellitus with proliferative diabetic retinopathy with traction retinal detachment not involving the macula, left eye",Type 1 diabetes mellitus with proliferative diabetic retinopathy with traction retinal detachment not involving the macula,9
E10354,2,E103542,"Type 1 diab with prolif diab rtnop with comb detach, l eye","Type 1 diabetes mellitus with proliferative diabetic retinopathy with combined traction retinal detachment and rhegmatogenous retinal detachment, left eye",Type 1 diabetes mellitus with proliferative diabetic retinopathy with combined traction retinal detachment and rhegmatogenous retinal detachment,9
E10355,2,E103552,"Type 1 diabetes with stable prolif diabetic rtnop, left eye","Type 1 diabetes mellitus with stable proliferative diabetic retinopathy, left eye",Type 1 diabetes mellitus with stable proliferative diabetic retinopathy,9
F65,2,F652,Exhibitionism,Exhibitionism,Paraphilias,9
E10359,2,E103592,"Type 1 diab with prolif diab rtnop without mclr edema, l eye","Type 1 diabetes mellitus with proliferative diabetic retinopathy without macular edema, left eye",Type 1 diabetes mellitus with proliferative diabetic retinopathy without macular edema,9
E104,2,E1042,Type 1 diabetes mellitus with diabetic polyneuropathy,Type 1 diabetes mellitus with diabetic polyneuropathy,Type 1 diabetes mellitus with neurological complications,9
E105,2,E1052,Type 1 diabetes w diabetic peripheral angiopathy w gangrene,Type 1 diabetes mellitus with diabetic peripheral angiopathy with gangrene,Type 1 diabetes mellitus with circulatory complications,9
E1062,2,E10622,Type 1 diabetes mellitus with other skin ulcer,Type 1 diabetes mellitus with other skin ulcer,Type 1 diabetes mellitus with skin complications,9
E112,2,E1122,Type 2 diabetes mellitus w diabetic chronic kidney disease,Type 2 diabetes mellitus with diabetic chronic kidney disease,Type 2 diabetes mellitus with kidney complications,9
E11321,2,E113212,"Type 2 diab with mild nonp rtnop with macular edema, l eye","Type 2 diabetes mellitus with mild nonproliferative diabetic retinopathy with macular edema, left eye",Type 2 diabetes mellitus with mild nonproliferative diabetic retinopathy with macular edema,9
E11329,2,E113292,"Type 2 diab with mild nonp rtnop without mclr edema, l eye","Type 2 diabetes mellitus with mild nonproliferative diabetic retinopathy without macular edema, left eye",Type 2 diabetes mellitus with mild nonproliferative diabetic retinopathy without macular edema,9
E11331,2,E113312,"Type 2 diab with mod nonp rtnop with macular edema, l eye","Type 2 diabetes mellitus with moderate nonproliferative diabetic retinopathy with macular edema, left eye",Type 2 diabetes mellitus with moderate nonproliferative diabetic retinopathy with macular edema,9
E11339,2,E113392,"Type 2 diab with mod nonp rtnop without macular edema, l eye","Type 2 diabetes mellitus with moderate nonproliferative diabetic retinopathy without macular edema, left eye",Type 2 diabetes mellitus with moderate nonproliferative diabetic retinopathy without macular edema,9
E11341,2,E113412,"Type 2 diab with severe nonp rtnop with macular edema, l eye","Type 2 diabetes mellitus with severe nonproliferative diabetic retinopathy with macular edema, left eye",Type 2 diabetes mellitus with severe nonproliferative diabetic retinopathy with macular edema,9
E11349,2,E113492,"Type 2 diab with severe nonp rtnop without mclr edema, l eye","Type 2 diabetes mellitus with severe nonproliferative diabetic retinopathy without macular edema, left eye",Type 2 diabetes mellitus with severe nonproliferative diabetic retinopathy without macular edema,9
E11351,2,E113512,"Type 2 diab with prolif diab rtnop with macular edema, l eye","Type 2 diabetes mellitus with proliferative diabetic retinopathy with macular edema, left eye",Type 2 diabetes mellitus with proliferative diabetic retinopathy with macular edema,9
E11352,2,E113522,"Type 2 diab w prolif diab rtnop w trctn dtch macula, l eye","Type 2 diabetes mellitus with proliferative diabetic retinopathy with traction retinal detachment involving the macula, left eye",Type 2 diabetes mellitus with proliferative diabetic retinopathy with traction retinal detachment involving the macula,9
E11353,2,E113532,"Type 2 diab w prolif diab rtnop w trctn dtch n-mcla, l eye","Type 2 diabetes mellitus with proliferative diabetic retinopathy with traction retinal detachment not involving the macula, left eye",Type 2 diabetes mellitus with proliferative diabetic retinopathy with traction retinal detachment not involving the macula,9
E11354,2,E113542,"Type 2 diab with prolif diab rtnop with comb detach, l eye","Type 2 diabetes mellitus with proliferative diabetic retinopathy with combined traction retinal detachment and rhegmatogenous retinal detachment, left eye",Type 2 diabetes mellitus with proliferative diabetic retinopathy with combined traction retinal detachment and rhegmatogenous retinal detachment,9
E11355,2,E113552,"Type 2 diabetes with stable prolif diabetic rtnop, left eye","Type 2 diabetes mellitus with stable proliferative diabetic retinopathy, left eye",Type 2 diabetes mellitus with stable proliferative diabetic retinopathy,9
E11359,2,E113592,"Type 2 diab with prolif diab rtnop without mclr edema, l eye","Type 2 diabetes mellitus with proliferative diabetic retinopathy without macular edema, left eye",Type 2 diabetes mellitus with proliferative diabetic retinopathy without macular edema,9
E114,2,E1142,Type 2 diabetes mellitus with diabetic polyneuropathy,Type 2 diabetes mellitus with diabetic polyneuropathy,Type 2 diabetes mellitus with neurological complications,9
E115,2,E1152,Type 2 diabetes w diabetic peripheral angiopathy w gangrene,Type 2 diabetes mellitus with diabetic peripheral angiopathy with gangrene,Type 2 diabetes mellitus with circulatory complications,9
E1162,2,E11622,Type 2 diabetes mellitus with other skin ulcer,Type 2 diabetes mellitus with other skin ulcer,Type 2 diabetes mellitus with skin complications,9
E132,2,E1322,Oth diabetes mellitus with diabetic chronic kidney disease,Other specified diabetes mellitus with diabetic chronic kidney disease,Other specified diabetes mellitus with kidney complications,9
E13321,2,E133212,"Oth diab with mild nonp rtnop with macular edema, left eye","Other specified diabetes mellitus with mild nonproliferative diabetic retinopathy with macular edema, left eye",Other specified diabetes mellitus with mild nonproliferative diabetic retinopathy with macular edema,9
E13329,2,E133292,"Oth diab with mild nonp rtnop without macular edema, l eye","Other specified diabetes mellitus with mild nonproliferative diabetic retinopathy without macular edema, left eye",Other specified diabetes mellitus with mild nonproliferative diabetic retinopathy without macular edema,9
E13331,2,E133312,"Oth diab with moderate nonp rtnop with macular edema, l eye","Other specified diabetes mellitus with moderate nonproliferative diabetic retinopathy with macular edema, left eye",Other specified diabetes mellitus with moderate nonproliferative diabetic retinopathy with macular edema,9
E13339,2,E133392,"Oth diab with mod nonp rtnop without macular edema, l eye","Other specified diabetes mellitus with moderate nonproliferative diabetic retinopathy without macular edema, left eye",Other specified diabetes mellitus with moderate nonproliferative diabetic retinopathy without macular edema,9
E13341,2,E133412,"Oth diab with severe nonp rtnop with macular edema, left eye","Other specified diabetes mellitus with severe nonproliferative diabetic retinopathy with macular edema, left eye",Other specified diabetes mellitus with severe nonproliferative diabetic retinopathy with macular edema,9
E13349,2,E133492,"Oth diab with severe nonp rtnop without macular edema, l eye","Other specified diabetes mellitus with severe nonproliferative diabetic retinopathy without macular edema, left eye",Other specified diabetes mellitus with severe nonproliferative diabetic retinopathy without macular edema,9
F655,2,F6552,Sexual sadism,Sexual sadism,Sadomasochism,9
E13351,2,E133512,"Oth diab with prolif diab rtnop with macular edema, left eye","Other specified diabetes mellitus with proliferative diabetic retinopathy with macular edema, left eye",Other specified diabetes mellitus with proliferative diabetic retinopathy with macular edema,9
E13352,2,E133522,"Oth diab w prolif diab rtnop with trctn dtch macula, l eye","Other specified diabetes mellitus with proliferative diabetic retinopathy with traction retinal detachment involving the macula, left eye",Other specified diabetes mellitus with proliferative diabetic retinopathy with traction retinal detachment involving the macula,9
E13353,2,E133532,"Oth diab w prolif diab rtnop with trctn dtch n-mcla, l eye","Other specified diabetes mellitus with proliferative diabetic retinopathy with traction retinal detachment not involving the macula, left eye",Other specified diabetes mellitus with proliferative diabetic retinopathy with traction retinal detachment not involving the macula,9
E13354,2,E133542,"Oth diab with prolif diab rtnop with comb detach, left eye","Other specified diabetes mellitus with proliferative diabetic retinopathy with combined traction retinal detachment and rhegmatogenous retinal detachment, left eye",Other specified diabetes mellitus with proliferative diabetic retinopathy with combined traction retinal detachment and rhegmatogenous retinal detachment,9
E13355,2,E133552,"Oth diabetes with stable prolif diabetic rtnop, left eye","Other specified diabetes mellitus with stable proliferative diabetic retinopathy, left eye",Other specified diabetes mellitus with stable proliferative diabetic retinopathy,9
E13359,2,E133592,"Oth diab with prolif diab rtnop without macular edema, l eye","Other specified diabetes mellitus with proliferative diabetic retinopathy without macular edema, left eye",Other specified diabetes mellitus with proliferative diabetic retinopathy without macular edema,9
E134,2,E1342,Oth diabetes mellitus with diabetic polyneuropathy,Other specified diabetes mellitus with diabetic polyneuropathy,Other specified diabetes mellitus with neurological complications,9
E135,2,E1352,Oth diabetes w diabetic peripheral angiopathy w gangrene,Other specified diabetes mellitus with diabetic peripheral angiopathy with gangrene,Other specified diabetes mellitus with circulatory complications,9
E1362,2,E13622,Other specified diabetes mellitus with other skin ulcer,Other specified diabetes mellitus with other skin ulcer,Other specified diabetes mellitus with skin complications,9
E16,2,E162,"Hypoglycemia, unspecified","Hypoglycemia, unspecified",Other disorders of pancreatic internal secretion,9
E21,2,E212,Other hyperparathyroidism,Other hyperparathyroidism,Hyperparathyroidism and other disorders of parathyroid gland,9
E22,2,E222,Syndrome of inappropriate secretion of antidiuretic hormone,Syndrome of inappropriate secretion of antidiuretic hormone,Hyperfunction of pituitary gland,9
E23,2,E232,Diabetes insipidus,Diabetes insipidus,Hypofunction and other disorders of the pituitary gland,9
E24,2,E242,Drug-induced Cushing's syndrome,Drug-induced Cushing's syndrome,Cushing's syndrome,9
E260,2,E2602,Glucocorticoid-remediable aldosteronism,Glucocorticoid-remediable aldosteronism,Primary hyperaldosteronism,9
E27,2,E272,Addisonian crisis,Addisonian crisis,Other disorders of adrenal gland,9
E28,2,E282,Polycystic ovarian syndrome,Polycystic ovarian syndrome,Ovarian dysfunction,9
E312,2,E3122,Multiple endocrine neoplasia [MEN] type IIA,Multiple endocrine neoplasia [MEN] type IIA,Multiple endocrine neoplasia [MEN] syndromes,9
E34,2,E342,"Ectopic hormone secretion, not elsewhere classified","Ectopic hormone secretion, not elsewhere classified",Other endocrine disorders,9
E345,2,E3452,Partial androgen insensitivity syndrome,Partial androgen insensitivity syndrome,Androgen insensitivity syndrome,9
E360,2,E3602,Intraop hemor/hemtom of an endo sys org comp oth procedure,Intraoperative hemorrhage and hematoma of an endocrine system organ or structure complicating other procedure,Intraoperative hemorrhage and hematoma of an endocrine system organ or structure complicating a procedure,9
E361,2,E3612,Acc pnctr & lac of an endo sys org during oth procedure,Accidental puncture and laceration of an endocrine system organ or structure during other procedure,Accidental puncture and laceration of an endocrine system organ or structure during a procedure,9
E50,2,E502,Vitamin A deficiency with corneal xerosis,Vitamin A deficiency with corneal xerosis,Vitamin A deficiency,9
E511,2,E5112,Wet beriberi,Wet beriberi,Beriberi,9
E61,2,E612,Magnesium deficiency,Magnesium deficiency,Deficiency of other nutrient elements,9
E64,2,E642,Sequelae of vitamin C deficiency,Sequelae of vitamin C deficiency,Sequelae of malnutrition and other nutritional deficiencies,9
E67,2,E672,Megavitamin-B6 syndrome,Megavitamin-B6 syndrome,Other hyperalimentation,9
E7131,2,E71312,Short chain acyl CoA dehydrogenase deficiency,Short chain acyl CoA dehydrogenase deficiency,Disorders of fatty-acid oxidation,9
E714,2,E7142,Carnitine deficiency due to inborn errors of metabolism,Carnitine deficiency due to inborn errors of metabolism,Disorders of carnitine metabolism,9
E7152,2,E71522,Adrenomyeloneuropathy,Adrenomyeloneuropathy,X-linked adrenoleukodystrophy,9
E7154,2,E71542,Other group 3 peroxisomal disorders,Other group 3 peroxisomal disorders,Other peroxisomal disorders,9
E720,2,E7202,Hartnup's disease,Hartnup's disease,Disorders of amino-acid transport,9
E721,2,E7212,Methylenetetrahydrofolate reductase deficiency,Methylenetetrahydrofolate reductase deficiency,Disorders of sulfur-bearing amino-acid metabolism,9
E722,2,E7222,Arginosuccinic aciduria,Arginosuccinic aciduria,Disorders of urea cycle metabolism,9
E725,2,E7252,Trimethylaminuria,Trimethylaminuria,Disorders of glycine metabolism,9
E740,2,E7402,Pompe disease,Pompe disease,Glycogen storage disease,9
E741,2,E7412,Hereditary fructose intolerance,Hereditary fructose intolerance,Disorders of fructose metabolism,9
E750,2,E7502,Tay-Sachs disease,Tay-Sachs disease,GM2 gangliosidosis,9
E752,2,E7522,Gaucher disease,Gaucher disease,Other sphingolipidosis,9
E7524,2,E75242,Niemann-Pick disease type C,Niemann-Pick disease type C,Niemann-Pick disease,9
E760,2,E7602,Hurler-Scheie syndrome,Hurler-Scheie syndrome,"Mucopolysaccharidosis, type I",9
E787,2,E7872,Smith-Lemli-Opitz syndrome,Smith-Lemli-Opitz syndrome,Disorders of bile acid and cholesterol metabolism,9
B023,3,B0233,Zoster keratitis,Zoster keratitis,Zoster ocular disease,9
E833,2,E8332,Hereditary vitamin D-dependent rickets (type 1) (type 2),Hereditary vitamin D-dependent rickets (type 1) (type 2),Disorders of phosphorus metabolism and phosphatases,9
E834,2,E8342,Hypomagnesemia,Hypomagnesemia,Disorders of magnesium metabolism,9
E835,2,E8352,Hypercalcemia,Hypercalcemia,Disorders of calcium metabolism,9
E85,2,E852,"Heredofamilial amyloidosis, unspecified","Heredofamilial amyloidosis, unspecified",Amyloidosis,9
E858,2,E8582,Wild-type transthyretin-related (ATTR) amyloidosis,Wild-type transthyretin-related (ATTR) amyloidosis,Other amyloidosis,9
E87,2,E872,Acidosis,Acidosis,"Other disorders of fluid, electrolyte and acid-base balance",9
E884,2,E8842,MERRF syndrome,MERRF syndrome,Mitochondrial metabolism disorders,9
E89,2,E892,Postprocedural hypoparathyroidism,Postprocedural hypoparathyroidism,"Postprocedural endocrine and metabolic complications and disorders, not elsewhere classified",9
E8982,2,E89822,Postproc seroma of an endo sys org fol an endo sys procedure,Postprocedural seroma of an endocrine system organ or structure following an endocrine system procedure,Postprocedural hematoma and seroma of an endocrine system organ or structure,9
F06,2,F062,Psychotic disorder w delusions due to known physiol cond,Psychotic disorder with delusions due to known physiological condition,Other mental disorders due to known physiological condition,9
F063,2,F0632,Mood disord d/t physiol cond w major depressive-like epsd,Mood disorder due to known physiological condition with major depressive-like episode,Mood disorder due to known physiological condition,9
F1018,2,F10182,Alcohol abuse with alcohol-induced sleep disorder,Alcohol abuse with alcohol-induced sleep disorder,Alcohol abuse with other alcohol-induced disorders,9
F1023,2,F10232,Alcohol dependence w withdrawal with perceptual disturbance,Alcohol dependence with withdrawal with perceptual disturbance,Alcohol dependence with withdrawal,9
F1028,2,F10282,Alcohol dependence with alcohol-induced sleep disorder,Alcohol dependence with alcohol-induced sleep disorder,Alcohol dependence with other alcohol-induced disorders,9
F1098,2,F10982,"Alcohol use, unspecified with alcohol-induced sleep disorder","Alcohol use, unspecified with alcohol-induced sleep disorder","Alcohol use, unspecified with other alcohol-induced disorders",9
F1112,2,F11122,Opioid abuse with intoxication with perceptual disturbance,Opioid abuse with intoxication with perceptual disturbance,Opioid abuse with intoxication,9
F1118,2,F11182,Opioid abuse with opioid-induced sleep disorder,Opioid abuse with opioid-induced sleep disorder,Opioid abuse with other opioid-induced disorder,9
F1122,2,F11222,Opioid dependence w intoxication with perceptual disturbance,Opioid dependence with intoxication with perceptual disturbance,Opioid dependence with intoxication,9
F1128,2,F11282,Opioid dependence with opioid-induced sleep disorder,Opioid dependence with opioid-induced sleep disorder,Opioid dependence with other opioid-induced disorder,9
F1192,2,F11922,"Opioid use, unsp w intoxication with perceptual disturbance","Opioid use, unspecified with intoxication with perceptual disturbance","Opioid use, unspecified with intoxication",9
F1198,2,F11982,"Opioid use, unspecified with opioid-induced sleep disorder","Opioid use, unspecified with opioid-induced sleep disorder","Opioid use, unspecified with other specified opioid-induced disorder",9
F1212,2,F12122,Cannabis abuse with intoxication with perceptual disturbance,Cannabis abuse with intoxication with perceptual disturbance,Cannabis abuse with intoxication,9
F1222,2,F12222,Cannabis dependence w intoxication w perceptual disturbance,Cannabis dependence with intoxication with perceptual disturbance,Cannabis dependence with intoxication,9
F1292,2,F12922,"Cannabis use, unsp w intoxication w perceptual disturbance","Cannabis use, unspecified with intoxication with perceptual disturbance","Cannabis use, unspecified with intoxication",9
F1318,2,F13182,"Sedative, hypnotic or anxiolytic abuse w sleep disorder","Sedative, hypnotic or anxiolytic abuse with sedative, hypnotic or anxiolytic-induced sleep disorder","Sedative, hypnotic or anxiolytic abuse with other sedative, hypnotic or anxiolytic-induced disorders",9
F1323,2,F13232,Sedatv/hyp/anxiolytc depend w w/drawal w perceptual disturb,"Sedative, hypnotic or anxiolytic dependence with withdrawal with perceptual disturbance","Sedative, hypnotic or anxiolytic dependence with withdrawal",9
F1328,2,F13282,"Sedative, hypnotic or anxiolytic dependence w sleep disorder","Sedative, hypnotic or anxiolytic dependence with sedative, hypnotic or anxiolytic-induced sleep disorder","Sedative, hypnotic or anxiolytic dependence with other sedative, hypnotic or anxiolytic-induced disorders",9
F1393,2,F13932,"Sedatv/hyp/anxiolytc use, unsp w w/drawal w perceptl disturb","Sedative, hypnotic or anxiolytic use, unspecified with withdrawal with perceptual disturbances","Sedative, hypnotic or anxiolytic use, unspecified with withdrawal",9
F1398,2,F13982,"Sedative, hypnotic or anxiolytic use, unsp w sleep disorder","Sedative, hypnotic or anxiolytic use, unspecified with sedative, hypnotic or anxiolytic-induced sleep disorder","Sedative, hypnotic or anxiolytic use, unspecified with other sedative, hypnotic or anxiolytic-induced disorders",9
F1412,2,F14122,Cocaine abuse with intoxication with perceptual disturbance,Cocaine abuse with intoxication with perceptual disturbance,Cocaine abuse with intoxication,9
F1418,2,F14182,Cocaine abuse with cocaine-induced sleep disorder,Cocaine abuse with cocaine-induced sleep disorder,Cocaine abuse with other cocaine-induced disorder,9
F1422,2,F14222,Cocaine dependence w intoxication w perceptual disturbance,Cocaine dependence with intoxication with perceptual disturbance,Cocaine dependence with intoxication,9
F1428,2,F14282,Cocaine dependence with cocaine-induced sleep disorder,Cocaine dependence with cocaine-induced sleep disorder,Cocaine dependence with other cocaine-induced disorder,9
F1492,2,F14922,"Cocaine use, unsp w intoxication with perceptual disturbance","Cocaine use, unspecified with intoxication with perceptual disturbance","Cocaine use, unspecified with intoxication",9
F1498,2,F14982,"Cocaine use, unspecified with cocaine-induced sleep disorder","Cocaine use, unspecified with cocaine-induced sleep disorder","Cocaine use, unspecified with other specified cocaine-induced disorder",9
F1512,2,F15122,Oth stimulant abuse w intoxication w perceptual disturbance,Other stimulant abuse with intoxication with perceptual disturbance,Other stimulant abuse with intoxication,9
F1518,2,F15182,Other stimulant abuse with stimulant-induced sleep disorder,Other stimulant abuse with stimulant-induced sleep disorder,Other stimulant abuse with other stimulant-induced disorder,9
F1522,2,F15222,Oth stimulant dependence w intox w perceptual disturbance,Other stimulant dependence with intoxication with perceptual disturbance,Other stimulant dependence with intoxication,9
F1528,2,F15282,Oth stimulant dependence w stimulant-induced sleep disorder,Other stimulant dependence with stimulant-induced sleep disorder,Other stimulant dependence with other stimulant-induced disorder,9
F1592,2,F15922,"Oth stimulant use, unsp w intox w perceptual disturbance","Other stimulant use, unspecified with intoxication with perceptual disturbance","Other stimulant use, unspecified with intoxication",9
F1598,2,F15982,"Oth stimulant use, unsp w stimulant-induced sleep disorder","Other stimulant use, unspecified with stimulant-induced sleep disorder","Other stimulant use, unspecified with other stimulant-induced disorder",9
F1612,2,F16122,Hallucinogen abuse w intoxication w perceptual disturbance,Hallucinogen abuse with intoxication with perceptual disturbance,Hallucinogen abuse with intoxication,9
F1912,2,F19122,Oth psychoactv substance abuse w intox w perceptual disturb,Other psychoactive substance abuse with intoxication with perceptual disturbances,Other psychoactive substance abuse with intoxication,9
F1918,2,F19182,Oth psychoactive substance abuse w sleep disorder,Other psychoactive substance abuse with psychoactive substance-induced sleep disorder,Other psychoactive substance abuse with other psychoactive substance-induced disorders,9
F1922,2,F19222,Oth psychoactv substance depend w intox w perceptual disturb,Other psychoactive substance dependence with intoxication with perceptual disturbance,Other psychoactive substance dependence with intoxication,9
F1923,2,F19232,Oth psychoactv sub depend w w/drawal w perceptl disturb,Other psychoactive substance dependence with withdrawal with perceptual disturbance,Other psychoactive substance dependence with withdrawal,9
F1928,2,F19282,Oth psychoactive substance dependence w sleep disorder,Other psychoactive substance dependence with psychoactive substance-induced sleep disorder,Other psychoactive substance dependence with other psychoactive substance-induced disorders,9
F1992,2,F19922,"Oth psychoactv sub use, unsp w intox w perceptl disturb","Other psychoactive substance use, unspecified with intoxication with perceptual disturbance","Other psychoactive substance use, unspecified with intoxication",9
F1993,2,F19932,"Oth psychoactv sub use, unsp w w/drawal w perceptl disturb","Other psychoactive substance use, unspecified with withdrawal with perceptual disturbance","Other psychoactive substance use, unspecified with withdrawal",9
F1998,2,F19982,"Oth psychoactive substance use, unsp w sleep disorder","Other psychoactive substance use, unspecified with psychoactive substance-induced sleep disorder","Other psychoactive substance use, unspecified with other psychoactive substance-induced disorders",9
F20,2,F202,Catatonic schizophrenia,Catatonic schizophrenia,Schizophrenia,9
F301,2,F3012,"Manic episode without psychotic symptoms, moderate","Manic episode without psychotic symptoms, moderate",Manic episode without psychotic symptoms,9
F311,2,F3112,"Bipolar disord, crnt episode manic w/o psych features, mod","Bipolar disorder, current episode manic without psychotic features, moderate","Bipolar disorder, current episode manic without psychotic features",9
F313,2,F3132,"Bipolar disorder, current episode depressed, moderate","Bipolar disorder, current episode depressed, moderate","Bipolar disorder, current episode depressed, mild or moderate severity",9
F316,2,F3162,"Bipolar disorder, current episode mixed, moderate","Bipolar disorder, current episode mixed, moderate","Bipolar disorder, current episode mixed",9
F317,2,F3172,"Bipolar disord, in full remis, most recent episode hypomanic","Bipolar disorder, in full remission, most recent episode hypomanic","Bipolar disorder, currently in remission",9
F32,2,F322,"Major depressv disord, single epsd, sev w/o psych features","Major depressive disorder, single episode, severe without psychotic features","Major depressive disorder, single episode",9
F33,2,F332,"Major depressv disorder, recurrent severe w/o psych features","Major depressive disorder, recurrent severe without psychotic features","Major depressive disorder, recurrent",9
F334,2,F3342,"Major depressive disorder, recurrent, in full remission","Major depressive disorder, recurrent, in full remission","Major depressive disorder, recurrent, in remission",9
F400,2,F4002,Agoraphobia without panic disorder,Agoraphobia without panic disorder,Agoraphobia,9
F4023,2,F40232,Fear of other medical care,Fear of other medical care,"Blood, injection, injury type phobia",9
F4024,2,F40242,Fear of bridges,Fear of bridges,Situational type phobia,9
F42,2,F422,Mixed obsessional thoughts and acts,Mixed obsessional thoughts and acts,Obsessive-compulsive disorder,9
F431,2,F4312,"Post-traumatic stress disorder, chronic","Post-traumatic stress disorder, chronic",Post-traumatic stress disorder (PTSD),9
F432,2,F4322,Adjustment disorder with anxiety,Adjustment disorder with anxiety,Adjustment disorders,9
F44,2,F442,Dissociative stupor,Dissociative stupor,Dissociative and conversion disorders,9
F452,2,F4522,Body dysmorphic disorder,Body dysmorphic disorder,Hypochondriacal disorders,9
F454,2,F4542,Pain disorder with related psychological factors,Pain disorder with related psychological factors,Pain disorders related to psychological factors,9
F48,2,F482,Pseudobulbar affect,Pseudobulbar affect,Other nonpsychotic mental disorders,9
F500,2,F5002,"Anorexia nervosa, binge eating/purging type","Anorexia nervosa, binge eating/purging type",Anorexia nervosa,9
F508,2,F5082,Avoidant/restrictive food intake disorder,Avoidant/restrictive food intake disorder,Other eating disorders,9
F510,2,F5102,Adjustment insomnia,Adjustment insomnia,Insomnia not due to a substance or known physiological condition,9
F511,2,F5112,Insufficient sleep syndrome,Insufficient sleep syndrome,Hypersomnia not due to a substance or known physiological condition,9
F522,2,F5222,Female sexual arousal disorder,Female sexual arousal disorder,Sexual arousal disorders,9
F523,2,F5232,Male orgasmic disorder,Male orgasmic disorder,Orgasmic disorder,9
F55,2,F552,Abuse of laxatives,Abuse of laxatives,Abuse of non-psychoactive substances,9
F60,2,F602,Antisocial personality disorder,Antisocial personality disorder,Specific personality disorders,9
F63,2,F632,Kleptomania,Kleptomania,Impulse disorders,9
F64,2,F642,Gender identity disorder of childhood,Gender identity disorder of childhood,Gender identity disorders,9
F681,2,F6812,Factitious disorder w predom physical signs and symptoms,Factitious disorder with predominantly physical signs and symptoms,Factitious disorder,9
F80,2,F802,Mixed receptive-expressive language disorder,Mixed receptive-expressive language disorder,Specific developmental disorders of speech and language,9
F808,2,F8082,Social pragmatic communication disorder,Social pragmatic communication disorder,Other developmental disorders of speech and language,9
F81,2,F812,Mathematics disorder,Mathematics disorder,Specific developmental disorders of scholastic skills,9
F84,2,F842,Rett's syndrome,Rett's syndrome,Pervasive developmental disorders,9
F90,2,F902,"Attention-deficit hyperactivity disorder, combined type","Attention-deficit hyperactivity disorder, combined type",Attention-deficit hyperactivity disorders,9
F91,2,F912,"Conduct disorder, adolescent-onset type","Conduct disorder, adolescent-onset type",Conduct disorders,9
F94,2,F942,Disinhibited attachment disorder of childhood,Disinhibited attachment disorder of childhood,Disorders of social functioning with onset specific to childhood and adolescence,9
F95,2,F952,Tourette's disorder,Tourette's disorder,Tic disorder,9
G00,2,G002,Streptococcal meningitis,Streptococcal meningitis,"Bacterial meningitis, not elsewhere classified",9
G03,2,G032,Benign recurrent meningitis [Mollaret],Benign recurrent meningitis [Mollaret],Meningitis due to other and unspecified causes,9
G040,2,G0402,"Postimmun ac dissem encphlts, myelitis and encephalomyelitis","Postimmunization acute disseminated encephalitis, myelitis and encephalomyelitis",Acute disseminated encephalitis and encephalomyelitis (ADEM),9
G043,2,G0432,Postimmun acute necrotizing hemorrhagic encephalopathy,Postimmunization acute necrotizing hemorrhagic encephalopathy,Acute necrotizing hemorrhagic encephalopathy,9
G06,2,G062,"Extradural and subdural abscess, unspecified","Extradural and subdural abscess, unspecified",Intracranial and intraspinal abscess and granuloma,9
G11,2,G112,Late-onset cerebellar ataxia,Late-onset cerebellar ataxia,Hereditary ataxia,9
G122,2,G1222,Progressive bulbar palsy,Progressive bulbar palsy,Motor neuron disease,9
G13,2,G132,Systemic atrophy primarily affecting the cnsl in myxedema,Systemic atrophy primarily affecting the central nervous system in myxedema,Systemic atrophies primarily affecting central nervous system in diseases classified elsewhere,9
G23,2,G232,Striatonigral degeneration,Striatonigral degeneration,Other degenerative diseases of basal ganglia,9
G240,2,G2402,Drug induced acute dystonia,Drug induced acute dystonia,Drug induced dystonia,9
G25,2,G252,Other specified forms of tremor,Other specified forms of tremor,Other extrapyramidal and movement disorders,9
G258,2,G2582,Stiff-man syndrome,Stiff-man syndrome,Other specified extrapyramidal and movement disorders,9
G318,2,G3182,Leigh's disease,Leigh's disease,Other specified degenerative diseases of nervous system,9
G37,2,G372,Central pontine myelinolysis,Central pontine myelinolysis,Other demyelinating diseases of central nervous system,9
G4080,2,G40802,"Other epilepsy, not intractable, without status epilepticus","Other epilepsy, not intractable, without status epilepticus",Other epilepsy,9
G4081,2,G40812,"Lennox-Gastaut syndrome, not intractable, w/o stat epi","Lennox-Gastaut syndrome, not intractable, without status epilepticus",Lennox-Gastaut syndrome,9
G4082,2,G40822,"Epileptic spasms, not intractable, w/o status epilepticus","Epileptic spasms, not intractable, without status epilepticus",Epileptic spasms,9
G445,2,G4452,New daily persistent headache (NDPH),New daily persistent headache (NDPH),Complicated headache syndromes,9
G448,2,G4482,Headache associated with sexual activity,Headache associated with sexual activity,Other specified headache syndromes,9
G45,2,G452,Multiple and bilateral precerebral artery syndromes,Multiple and bilateral precerebral artery syndromes,Transient cerebral ischemic attacks and related syndromes,9
G46,2,G462,Posterior cerebral artery syndrome,Posterior cerebral artery syndrome,Vascular syndromes of brain in cerebrovascular diseases,9
G471,2,G4712,Idiopathic hypersomnia without long sleep time,Idiopathic hypersomnia without long sleep time,Hypersomnia,9
G472,2,G4722,"Circadian rhythm sleep disorder, advanced sleep phase type","Circadian rhythm sleep disorder, advanced sleep phase type",Circadian rhythm sleep disorders,9
G473,2,G4732,High altitude periodic breathing,High altitude periodic breathing,Sleep apnea,9
G475,2,G4752,REM sleep behavior disorder,REM sleep behavior disorder,Parasomnia,9
G476,2,G4762,Sleep related leg cramps,Sleep related leg cramps,Sleep related movement disorders,9
G51,2,G512,Melkersson's syndrome,Melkersson's syndrome,Facial nerve disorders,9
G52,2,G522,Disorders of vagus nerve,Disorders of vagus nerve,Disorders of other cranial nerves,9
G54,2,G542,"Cervical root disorders, not elsewhere classified","Cervical root disorders, not elsewhere classified",Nerve root and plexus disorders,9
G560,2,G5602,"Carpal tunnel syndrome, left upper limb","Carpal tunnel syndrome, left upper limb",Carpal tunnel syndrome,9
G561,2,G5612,"Other lesions of median nerve, left upper limb","Other lesions of median nerve, left upper limb",Other lesions of median nerve,9
G562,2,G5622,"Lesion of ulnar nerve, left upper limb","Lesion of ulnar nerve, left upper limb",Lesion of ulnar nerve,9
G563,2,G5632,"Lesion of radial nerve, left upper limb","Lesion of radial nerve, left upper limb",Lesion of radial nerve,9
G564,2,G5642,Causalgia of left upper limb,Causalgia of left upper limb,Causalgia of upper limb,9
G568,2,G5682,Other specified mononeuropathies of left upper limb,Other specified mononeuropathies of left upper limb,Other specified mononeuropathies of upper limb,9
G569,2,G5692,Unspecified mononeuropathy of left upper limb,Unspecified mononeuropathy of left upper limb,Unspecified mononeuropathy of upper limb,9
G570,2,G5702,"Lesion of sciatic nerve, left lower limb","Lesion of sciatic nerve, left lower limb",Lesion of sciatic nerve,9
G571,2,G5712,"Meralgia paresthetica, left lower limb","Meralgia paresthetica, left lower limb",Meralgia paresthetica,9
G572,2,G5722,"Lesion of femoral nerve, left lower limb","Lesion of femoral nerve, left lower limb",Lesion of femoral nerve,9
B05,3,B053,Measles complicated by otitis media,Measles complicated by otitis media,Measles,9
G573,2,G5732,"Lesion of lateral popliteal nerve, left lower limb","Lesion of lateral popliteal nerve, left lower limb",Lesion of lateral popliteal nerve,9
G574,2,G5742,"Lesion of medial popliteal nerve, left lower limb","Lesion of medial popliteal nerve, left lower limb",Lesion of medial popliteal nerve,9
G575,2,G5752,"Tarsal tunnel syndrome, left lower limb","Tarsal tunnel syndrome, left lower limb",Tarsal tunnel syndrome,9
G576,2,G5762,"Lesion of plantar nerve, left lower limb","Lesion of plantar nerve, left lower limb",Lesion of plantar nerve,9
G577,2,G5772,Causalgia of left lower limb,Causalgia of left lower limb,Causalgia of lower limb,9
G578,2,G5782,Other specified mononeuropathies of left lower limb,Other specified mononeuropathies of left lower limb,Other specified mononeuropathies of lower limb,9
A010,3,A0103,Typhoid pneumonia,Typhoid pneumonia,Typhoid fever,9
A022,3,A0223,Salmonella arthritis,Salmonella arthritis,Localized salmonella infections,9
A03,3,A033,Shigellosis due to Shigella sonnei,Shigellosis due to Shigella sonnei,Shigellosis,9
A04,3,A043,Enterohemorrhagic Escherichia coli infection,Enterohemorrhagic Escherichia coli infection,Other bacterial intestinal infections,9
A05,3,A053,Foodborne Vibrio parahaemolyticus intoxication,Foodborne Vibrio parahaemolyticus intoxication,"Other bacterial foodborne intoxications, not elsewhere classified",9
A06,3,A063,Ameboma of intestine,Ameboma of intestine,Amebiasis,9
A07,3,A073,Isosporiasis,Isosporiasis,Other protozoal intestinal diseases,9
A178,3,A1783,Tuberculous neuritis,Tuberculous neuritis,Other tuberculosis of nervous system,9
A180,3,A1803,Tuberculosis of other bones,Tuberculosis of other bones,Tuberculosis of bones and joints,9
A181,3,A1813,Tuberculosis of other urinary organs,Tuberculosis of other urinary organs,Tuberculosis of genitourinary system,9
A185,3,A1853,Tuberculous chorioretinitis,Tuberculous chorioretinitis,Tuberculosis of eye,9
A188,3,A1883,"Tuberculosis of digestive tract organs, NEC","Tuberculosis of digestive tract organs, not elsewhere classified",Tuberculosis of other specified organs,9
A20,3,A203,Plague meningitis,Plague meningitis,Plague,9
A21,3,A213,Gastrointestinal tularemia,Gastrointestinal tularemia,Tularemia,9
A23,3,A233,Brucellosis due to Brucella canis,Brucellosis due to Brucella canis,Brucellosis,9
A24,3,A243,Other melioidosis,Other melioidosis,Glanders and melioidosis,9
A30,3,A303,Borderline leprosy,Borderline leprosy,Leprosy [Hansen's disease],9
A36,3,A363,Cutaneous diphtheria,Cutaneous diphtheria,Diphtheria,9
A368,3,A3683,Diphtheritic polyneuritis,Diphtheritic polyneuritis,Other diphtheria,9
A39,3,A393,Chronic meningococcemia,Chronic meningococcemia,Meningococcal infection,9
A395,3,A3953,Meningococcal pericarditis,Meningococcal pericarditis,Meningococcal heart disease,9
A398,3,A3983,Meningococcal arthritis,Meningococcal arthritis,Other meningococcal infections,9
A40,3,A403,Sepsis due to Streptococcus pneumoniae,Sepsis due to Streptococcus pneumoniae,Streptococcal sepsis,9
A415,3,A4153,Sepsis due to Serratia,Sepsis due to Serratia,Sepsis due to other Gram-negative organisms,9
A48,3,A483,Toxic shock syndrome,Toxic shock syndrome,"Other bacterial diseases, not elsewhere classified",9
A500,3,A5003,Early congenital syphilitic pharyngitis,Early congenital syphilitic pharyngitis,"Early congenital syphilis, symptomatic",9
A504,3,A5043,Late congenital syphilitic polyneuropathy,Late congenital syphilitic polyneuropathy,Late congenital neurosyphilis [juvenile neurosyphilis],9
A505,3,A5053,Hutchinson's triad,Hutchinson's triad,"Other late congenital syphilis, symptomatic",9
A514,3,A5143,Secondary syphilitic oculopathy,Secondary syphilitic oculopathy,Other secondary syphilis,9
A520,3,A5203,Syphilitic endocarditis,Syphilitic endocarditis,Cardiovascular and cerebrovascular syphilis,9
A521,3,A5213,Late syphilitic meningitis,Late syphilitic meningitis,Symptomatic neurosyphilis,9
A527,3,A5273,Symptomatic late syphilis of other respiratory organs,Symptomatic late syphilis of other respiratory organs,Other symptomatic late syphilis,9
A540,3,A5403,"Gonococcal cervicitis, unspecified","Gonococcal cervicitis, unspecified",Gonococcal infection of lower genitourinary tract without periurethral or accessory gland abscess,9
A542,3,A5423,Gonococcal infection of other male genital organs,Gonococcal infection of other male genital organs,Gonococcal pelviperitonitis and other gonococcal genitourinary infection,9
A543,3,A5433,Gonococcal keratitis,Gonococcal keratitis,Gonococcal infection of eye,9
A544,3,A5443,Gonococcal osteomyelitis,Gonococcal osteomyelitis,Gonococcal infection of musculoskeletal system,9
A548,3,A5483,Gonococcal heart infection,Gonococcal heart infection,Other gonococcal infections,9
A590,3,A5903,Trichomonal cystitis and urethritis,Trichomonal cystitis and urethritis,Urogenital trichomoniasis,9
A600,3,A6003,Herpesviral cervicitis,Herpesviral cervicitis,Herpesviral infection of genitalia and urogenital tract,9
A66,3,A663,Hyperkeratosis of yaws,Hyperkeratosis of yaws,Yaws,9
A67,3,A673,Mixed lesions of pinta,Mixed lesions of pinta,Pinta [carate],9
A692,3,A6923,Arthritis due to Lyme disease,Arthritis due to Lyme disease,Lyme disease,9
A75,3,A753,Typhus fever due to Rickettsia tsutsugamushi,Typhus fever due to Rickettsia tsutsugamushi,Typhus fever,9
A77,3,A773,Spotted fever due to Rickettsia australis,Spotted fever due to Rickettsia australis,Spotted fever [tick-borne rickettsioses],9
A818,3,A8183,Fatal familial insomnia,Fatal familial insomnia,Other atypical virus infections of central nervous system,9
A83,3,A833,St Louis encephalitis,St Louis encephalitis,Mosquito-borne viral encephalitis,9
A98,3,A983,Marburg virus disease,Marburg virus disease,"Other viral hemorrhagic fevers, not elsewhere classified",9
B00,3,B003,Herpesviral meningitis,Herpesviral meningitis,Herpesviral [herpes simplex] infections,9
B005,3,B0053,Herpesviral conjunctivitis,Herpesviral conjunctivitis,Herpesviral ocular disease,9
B022,3,B0223,Postherpetic polyneuropathy,Postherpetic polyneuropathy,Zoster with other nervous system involvement,9
B30,3,B303,Acute epidemic hemorrhagic conjunctivitis (enteroviral),Acute epidemic hemorrhagic conjunctivitis (enteroviral),Viral conjunctivitis,9
B332,3,B3323,Viral pericarditis,Viral pericarditis,Viral carditis,9
B34,3,B343,"Parvovirus infection, unspecified","Parvovirus infection, unspecified",Viral infection of unspecified site,9
B35,3,B353,Tinea pedis,Tinea pedis,Dermatophytosis,9
B36,3,B363,Black piedra,Black piedra,Other superficial mycoses,9
B37,3,B373,Candidiasis of vulva and vagina,Candidiasis of vulva and vagina,Candidiasis,9
B378,3,B3783,Candidal cheilitis,Candidal cheilitis,Candidiasis of other sites,9
B38,3,B383,Cutaneous coccidioidomycosis,Cutaneous coccidioidomycosis,Coccidioidomycosis,9
B39,3,B393,Disseminated histoplasmosis capsulati,Disseminated histoplasmosis capsulati,Histoplasmosis,9
B40,3,B403,Cutaneous blastomycosis,Cutaneous blastomycosis,Blastomycosis,9
B45,3,B453,Osseous cryptococcosis,Osseous cryptococcosis,Cryptococcosis,9
B46,3,B463,Cutaneous mucormycosis,Cutaneous mucormycosis,Zygomycosis,9
B48,3,B483,Geotrichosis,Geotrichosis,"Other mycoses, not elsewhere classified",9
B588,3,B5883,Toxoplasma tubulo-interstitial nephropathy,Toxoplasma tubulo-interstitial nephropathy,Toxoplasmosis with other organ involvement,9
B601,3,B6013,Keratoconjunctivitis due to Acanthamoeba,Keratoconjunctivitis due to Acanthamoeba,Acanthamebiasis,9
B65,3,B653,Cercarial dermatitis,Cercarial dermatitis,Schistosomiasis [bilharziasis],9
B66,3,B663,Fascioliasis,Fascioliasis,Other fluke infections,9
B74,3,B743,Loiasis,Loiasis,Filariasis,9
B81,3,B813,Intestinal angiostrongyliasis,Intestinal angiostrongyliasis,"Other intestinal helminthiases, not elsewhere classified",9
B83,3,B833,Syngamiasis,Syngamiasis,Other helminthiases,9
B85,3,B853,Phthiriasis,Phthiriasis,Pediculosis and phthiriasis,9
B87,3,B873,Nasopharyngeal myiasis,Nasopharyngeal myiasis,Myiasis,9
B88,3,B883,External hirudiniasis,External hirudiniasis,Other infestations,9
B95,3,B953,Streptococcus pneumoniae causing diseases classd elswhr,Streptococcus pneumoniae as the cause of diseases classified elsewhere,"Streptococcus, Staphylococcus, and Enterococcus as the cause of diseases classified elsewhere",9
B962,3,B9623,Unsp shiga toxin E coli (STEC) causing dis classd elswhr,Unspecified Shiga toxin-producing Escherichia coli [E. coli] (STEC) as the cause of diseases classified elsewhere,Escherichia coli [E. coli ] as the cause of diseases classified elsewhere,9
B973,3,B9733,HTLV-I as the cause of diseases classified elsewhere,"Human T-cell lymphotrophic virus, type I [HTLV-I] as the cause of diseases classified elsewhere",Retrovirus as the cause of diseases classified elsewhere,9
C00,3,C003,"Malignant neoplasm of upper lip, inner aspect","Malignant neoplasm of upper lip, inner aspect",Malignant neoplasm of lip,9
C02,3,C023,"Malig neoplasm of anterior two-thirds of tongue, part unsp","Malignant neoplasm of anterior two-thirds of tongue, part unspecified",Malignant neoplasm of other and unspecified parts of tongue,9
C10,3,C103,Malignant neoplasm of posterior wall of oropharynx,Malignant neoplasm of posterior wall of oropharynx,Malignant neoplasm of oropharynx,9
C11,3,C113,Malignant neoplasm of anterior wall of nasopharynx,Malignant neoplasm of anterior wall of nasopharynx,Malignant neoplasm of nasopharynx,9
C15,3,C153,Malignant neoplasm of upper third of esophagus,Malignant neoplasm of upper third of esophagus,Malignant neoplasm of esophagus,9
C16,3,C163,Malignant neoplasm of pyloric antrum,Malignant neoplasm of pyloric antrum,Malignant neoplasm of stomach,9
C17,3,C173,"Meckel''s diverticulum, malignant","Meckel''s diverticulum, malignant",Malignant neoplasm of small intestine,9
C18,3,C183,Malignant neoplasm of hepatic flexure,Malignant neoplasm of hepatic flexure,Malignant neoplasm of colon,9
C22,3,C223,Angiosarcoma of liver,Angiosarcoma of liver,Malignant neoplasm of liver and intrahepatic bile ducts,9
C25,3,C253,Malignant neoplasm of pancreatic duct,Malignant neoplasm of pancreatic duct,Malignant neoplasm of pancreas,9
C31,3,C313,Malignant neoplasm of sphenoid sinus,Malignant neoplasm of sphenoid sinus,Malignant neoplasm of accessory sinuses,9
C32,3,C323,Malignant neoplasm of laryngeal cartilage,Malignant neoplasm of laryngeal cartilage,Malignant neoplasm of larynx,9
C38,3,C383,"Malignant neoplasm of mediastinum, part unspecified","Malignant neoplasm of mediastinum, part unspecified","Malignant neoplasm of heart, mediastinum and pleura",9
C41,3,C413,"Malignant neoplasm of ribs, sternum and clavicle","Malignant neoplasm of ribs, sternum and clavicle",Malignant neoplasm of bone and articular cartilage of other and unspecified sites,9
C46,3,C463,Kaposi's sarcoma of lymph nodes,Kaposi's sarcoma of lymph nodes,Kaposi's sarcoma,9
C49A,3,C49A3,Gastrointestinal stromal tumor of small intestine,Gastrointestinal stromal tumor of small intestine,Gastrointestinal stromal tumor,9
C54,3,C543,Malignant neoplasm of fundus uteri,Malignant neoplasm of fundus uteri,Malignant neoplasm of corpus uteri,9
C67,3,C673,Malignant neoplasm of anterior wall of bladder,Malignant neoplasm of anterior wall of bladder,Malignant neoplasm of bladder,9
C71,3,C713,Malignant neoplasm of parietal lobe,Malignant neoplasm of parietal lobe,Malignant neoplasm of brain,9
C75,3,C753,Malignant neoplasm of pineal gland,Malignant neoplasm of pineal gland,Malignant neoplasm of other endocrine glands and related structures,9
C7A02,3,C7A023,Malignant carcinoid tumor of the transverse colon,Malignant carcinoid tumor of the transverse colon,"Malignant carcinoid tumors of the appendix, large intestine, and rectum",9
C7A09,3,C7A093,Malignant carcinoid tumor of the kidney,Malignant carcinoid tumor of the kidney,Malignant carcinoid tumors of other sites,9
C7B0,3,C7B03,Secondary carcinoid tumors of bone,Secondary carcinoid tumors of bone,Secondary carcinoid tumors,9
C76,3,C763,Malignant neoplasm of pelvis,Malignant neoplasm of pelvis,Malignant neoplasm of other and ill-defined sites,9
C77,3,C773,Sec and unsp malig neoplasm of axilla and upper limb nodes,Secondary and unspecified malignant neoplasm of axilla and upper limb lymph nodes,Secondary and unspecified malignant neoplasm of lymph nodes,9
C810,3,C8103,"Nodular lymphocyte predom Hodgkin lymphoma, intra-abd nodes","Nodular lymphocyte predominant Hodgkin lymphoma, intra-abdominal lymph nodes",Nodular lymphocyte predominant Hodgkin lymphoma,9
C811,3,C8113,"Nodular sclerosis Hodgkin lymphoma, intra-abd lymph nodes","Nodular sclerosis Hodgkin lymphoma, intra-abdominal lymph nodes",Nodular sclerosis Hodgkin lymphoma,9
C812,3,C8123,"Mixed cellularity Hodgkin lymphoma, intra-abd lymph nodes","Mixed cellularity Hodgkin lymphoma, intra-abdominal lymph nodes",Mixed cellularity Hodgkin lymphoma,9
C813,3,C8133,"Lymphocyte depleted Hodgkin lymphoma, intra-abd lymph nodes","Lymphocyte depleted Hodgkin lymphoma, intra-abdominal lymph nodes",Lymphocyte depleted Hodgkin lymphoma,9
C814,3,C8143,"Lymphocyte-rich Hodgkin lymphoma, intra-abd lymph nodes","Lymphocyte-rich Hodgkin lymphoma, intra-abdominal lymph nodes",Lymphocyte-rich Hodgkin lymphoma,9
C817,3,C8173,"Other Hodgkin lymphoma, intra-abdominal lymph nodes","Other Hodgkin lymphoma, intra-abdominal lymph nodes",Other Hodgkin lymphoma,9
C819,3,C8193,"Hodgkin lymphoma, unspecified, intra-abdominal lymph nodes","Hodgkin lymphoma, unspecified, intra-abdominal lymph nodes","Hodgkin lymphoma, unspecified",9
C820,3,C8203,"Follicular lymphoma grade I, intra-abdominal lymph nodes","Follicular lymphoma grade I, intra-abdominal lymph nodes",Follicular lymphoma grade I,9
C821,3,C8213,"Follicular lymphoma grade II, intra-abdominal lymph nodes","Follicular lymphoma grade II, intra-abdominal lymph nodes",Follicular lymphoma grade II,9
C822,3,C8223,"Follicular lymphoma grade III, unsp, intra-abd lymph nodes","Follicular lymphoma grade III, unspecified, intra-abdominal lymph nodes","Follicular lymphoma grade III, unspecified",9
C823,3,C8233,"Follicular lymphoma grade IIIa, intra-abdominal lymph nodes","Follicular lymphoma grade IIIa, intra-abdominal lymph nodes",Follicular lymphoma grade IIIa,9
C824,3,C8243,"Follicular lymphoma grade IIIb, intra-abdominal lymph nodes","Follicular lymphoma grade IIIb, intra-abdominal lymph nodes",Follicular lymphoma grade IIIb,9
C825,3,C8253,"Diffuse follicle center lymphoma, intra-abd lymph nodes","Diffuse follicle center lymphoma, intra-abdominal lymph nodes",Diffuse follicle center lymphoma,9
C826,3,C8263,"Cutaneous follicle center lymphoma, intra-abd lymph nodes","Cutaneous follicle center lymphoma, intra-abdominal lymph nodes",Cutaneous follicle center lymphoma,9
C828,3,C8283,"Oth types of follicular lymphoma, intra-abd lymph nodes","Other types of follicular lymphoma, intra-abdominal lymph nodes",Other types of follicular lymphoma,9
C829,3,C8293,"Follicular lymphoma, unsp, intra-abdominal lymph nodes","Follicular lymphoma, unspecified, intra-abdominal lymph nodes","Follicular lymphoma, unspecified",9
C830,3,C8303,"Small cell B-cell lymphoma, intra-abdominal lymph nodes","Small cell B-cell lymphoma, intra-abdominal lymph nodes",Small cell B-cell lymphoma,9
C831,3,C8313,"Mantle cell lymphoma, intra-abdominal lymph nodes","Mantle cell lymphoma, intra-abdominal lymph nodes",Mantle cell lymphoma,9
C833,3,C8333,"Diffuse large B-cell lymphoma, intra-abdominal lymph nodes","Diffuse large B-cell lymphoma, intra-abdominal lymph nodes",Diffuse large B-cell lymphoma,9
C835,3,C8353,"Lymphoblastic (diffuse) lymphoma, intra-abd lymph nodes","Lymphoblastic (diffuse) lymphoma, intra-abdominal lymph nodes",Lymphoblastic (diffuse) lymphoma,9
C837,3,C8373,"Burkitt lymphoma, intra-abdominal lymph nodes","Burkitt lymphoma, intra-abdominal lymph nodes",Burkitt lymphoma,9
C838,3,C8383,"Other non-follicular lymphoma, intra-abdominal lymph nodes","Other non-follicular lymphoma, intra-abdominal lymph nodes",Other non-follicular lymphoma,9
C839,3,C8393,"Non-follic (diffuse) lymphoma, unsp, intra-abd lymph nodes","Non-follicular (diffuse) lymphoma, unspecified, intra-abdominal lymph nodes","Non-follicular (diffuse) lymphoma, unspecified",9
C840,3,C8403,"Mycosis fungoides, intra-abdominal lymph nodes","Mycosis fungoides, intra-abdominal lymph nodes",Mycosis fungoides,9
C841,3,C8413,"Sezary disease, intra-abdominal lymph nodes","Sezary disease, intra-abdominal lymph nodes",Sezary disease,9
C844,3,C8443,"Peripheral T-cell lymphoma, not classified, intra-abd nodes","Peripheral T-cell lymphoma, not classified, intra-abdominal lymph nodes","Peripheral T-cell lymphoma, not classified",9
C846,3,C8463,"Anaplastic large cell lymphoma, ALK-pos, intra-abd nodes","Anaplastic large cell lymphoma, ALK-positive, intra-abdominal lymph nodes","Anaplastic large cell lymphoma, ALK-positive",9
C847,3,C8473,"Anaplastic large cell lymphoma, ALK-neg, intra-abd nodes","Anaplastic large cell lymphoma, ALK-negative, intra-abdominal lymph nodes","Anaplastic large cell lymphoma, ALK-negative",9
C84A,3,C84A3,"Cutaneous T-cell lymphoma, unsp, intra-abdominal lymph nodes","Cutaneous T-cell lymphoma, unspecified, intra-abdominal lymph nodes","Cutaneous T-cell lymphoma, unspecified",9
C84Z,3,C84Z3,"Oth mature T/NK-cell lymphomas, intra-abdominal lymph nodes","Other mature T/NK-cell lymphomas, intra-abdominal lymph nodes",Other mature T/NK-cell lymphomas,9
C849,3,C8493,"Mature T/NK-cell lymphomas, unsp, intra-abd lymph nodes","Mature T/NK-cell lymphomas, unspecified, intra-abdominal lymph nodes","Mature T/NK-cell lymphomas, unspecified",9
C851,3,C8513,"Unspecified B-cell lymphoma, intra-abdominal lymph nodes","Unspecified B-cell lymphoma, intra-abdominal lymph nodes",Unspecified B-cell lymphoma,9
C852,3,C8523,"Mediastinal (thymic) large B-cell lymphoma, intra-abd nodes","Mediastinal (thymic) large B-cell lymphoma, intra-abdominal lymph nodes",Mediastinal (thymic) large B-cell lymphoma,9
C858,3,C8583,"Oth types of non-Hodgkin lymphoma, intra-abd lymph nodes","Other specified types of non-Hodgkin lymphoma, intra-abdominal lymph nodes",Other specified types of non-Hodgkin lymphoma,9
C859,3,C8593,"Non-Hodgkin lymphoma, unsp, intra-abdominal lymph nodes","Non-Hodgkin lymphoma, unspecified, intra-abdominal lymph nodes","Non-Hodgkin lymphoma, unspecified",9
C86,3,C863,Subcutaneous panniculitis-like T-cell lymphoma,Subcutaneous panniculitis-like T-cell lymphoma,Other specified types of T/NK-cell lymphoma,9
C88,3,C883,Immunoproliferative small intestinal disease,Immunoproliferative small intestinal disease,Malignant immunoproliferative diseases and certain other B-cell lymphomas,9
D000,3,D0003,Carcinoma in situ of gingiva and edentulous alveolar ridge,Carcinoma in situ of gingiva and edentulous alveolar ridge,"Carcinoma in situ of lip, oral cavity and pharynx",9
D01,3,D013,Carcinoma in situ of anus and anal canal,Carcinoma in situ of anus and anal canal,Carcinoma in situ of other and unspecified digestive organs,9
E03,4,E034,Atrophy of thyroid (acquired),Atrophy of thyroid (acquired),Other hypothyroidism,9
D12,3,D123,Benign neoplasm of transverse colon,Benign neoplasm of transverse colon,"Benign neoplasm of colon, rectum, anus and anal canal",9
D172,3,D1723,"Benign lipomatous neoplasm of skin, subcu of right leg",Benign lipomatous neoplasm of skin and subcutaneous tissue of right leg,Benign lipomatous neoplasm of skin and subcutaneous tissue of limb,9
D180,3,D1803,Hemangioma of intra-abdominal structures,Hemangioma of intra-abdominal structures,Hemangioma,9
D33,3,D333,Benign neoplasm of cranial nerves,Benign neoplasm of cranial nerves,Benign neoplasm of brain and other parts of central nervous system,9
D361,3,D3613,"Ben neoplm of prph nrv & autonm nrv sys of low lmb, inc hip","Benign neoplasm of peripheral nerves and autonomic nervous system of lower limb, including hip",Benign neoplasm of peripheral nerves and autonomic nervous system,9
D3A02,3,D3A023,Benign carcinoid tumor of the transverse colon,Benign carcinoid tumor of the transverse colon,"Benign carcinoid tumors of the appendix, large intestine, and rectum",9
D3A09,3,D3A093,Benign carcinoid tumor of the kidney,Benign carcinoid tumor of the kidney,Benign carcinoid tumors of other sites,9
D38,3,D383,Neoplasm of uncertain behavior of mediastinum,Neoplasm of uncertain behavior of mediastinum,Neoplasm of uncertain behavior of middle ear and respiratory and intrathoracic organs,9
D43,3,D433,Neoplasm of uncertain behavior of cranial nerves,Neoplasm of uncertain behavior of cranial nerves,Neoplasm of uncertain behavior of brain and central nervous system,9
D48,3,D483,Neoplasm of uncertain behavior of retroperitoneum,Neoplasm of uncertain behavior of retroperitoneum,Neoplasm of uncertain behavior of other and unspecified sites,9
D49,3,D493,Neoplasm of unspecified behavior of breast,Neoplasm of unspecified behavior of breast,Neoplasms of unspecified behavior,9
D51,3,D513,Other dietary vitamin B12 deficiency anemia,Other dietary vitamin B12 deficiency anemia,Vitamin B12 deficiency anemia,9
D55,3,D553,Anemia due to disorders of nucleotide metabolism,Anemia due to disorders of nucleotide metabolism,Anemia due to enzyme disorders,9
D56,3,D563,Thalassemia minor,Thalassemia minor,Thalassemia,9
D59,3,D593,Hemolytic-uremic syndrome,Hemolytic-uremic syndrome,Acquired hemolytic anemia,9
D64,3,D643,Other sideroblastic anemias,Other sideroblastic anemias,Other anemias,9
D69,3,D693,Immune thrombocytopenic purpura,Immune thrombocytopenic purpura,Purpura and other hemorrhagic conditions,9
D70,3,D703,Neutropenia due to infection,Neutropenia due to infection,Neutropenia,9
D7282,3,D72823,Leukemoid reaction,Leukemoid reaction,Elevated white blood cell count,9
D73,3,D733,Abscess of spleen,Abscess of spleen,Diseases of spleen,9
D76,3,D763,Other histiocytosis syndromes,Other histiocytosis syndromes,Other specified diseases with participation of lymphoreticular and reticulohistiocytic tissue,9
D783,3,D7833,Postprocedural seroma of the spleen fol proc on spleen,Postprocedural seroma of the spleen following a procedure on the spleen,Postprocedural hematoma and seroma of the spleen following a procedure,9
D80,3,D803,Selective deficiency of immunoglobulin G [IgG] subclasses,Selective deficiency of immunoglobulin G [IgG] subclasses,Immunodeficiency with predominantly antibody defects,9
D81,3,D813,Adenosine deaminase [ADA] deficiency,Adenosine deaminase [ADA] deficiency,Combined immunodeficiencies,9
D82,3,D823,Immunodef fol heredit defctv response to Epstein-Barr virus,Immunodeficiency following hereditary defective response to Epstein-Barr virus,Immunodeficiency associated with other major defects,9
D86,3,D863,Sarcoidosis of skin,Sarcoidosis of skin,Sarcoidosis,9
D868,3,D8683,Sarcoid iridocyclitis,Sarcoid iridocyclitis,Sarcoidosis of other sites,9
D89,3,D893,Immune reconstitution syndrome,Immune reconstitution syndrome,"Other disorders involving the immune mechanism, not elsewhere classified",9
D894,3,D8943,Secondary mast cell activation,Secondary mast cell activation,Mast cell activation syndrome and related disorders,9
D8981,3,D89813,"Graft-versus-host disease, unspecified","Graft-versus-host disease, unspecified",Graft-versus-host disease,9
E03,3,E033,Postinfectious hypothyroidism,Postinfectious hypothyroidism,Other hypothyroidism,9
E06,3,E063,Autoimmune thyroiditis,Autoimmune thyroiditis,Thyroiditis,9
E08321,3,E083213,"Diabetes with mild nonp rtnop with macular edema, bilateral","Diabetes mellitus due to underlying condition with mild nonproliferative diabetic retinopathy with macular edema, bilateral",Diabetes mellitus due to underlying condition with mild nonproliferative diabetic retinopathy with macular edema,9
E08329,3,E083293,"Diabetes with mild nonp rtnop without macular edema, bi","Diabetes mellitus due to underlying condition with mild nonproliferative diabetic retinopathy without macular edema, bilateral",Diabetes mellitus due to underlying condition with mild nonproliferative diabetic retinopathy without macular edema,9
E08331,3,E083313,"Diabetes with moderate nonp rtnop with macular edema, bi","Diabetes mellitus due to underlying condition with moderate nonproliferative diabetic retinopathy with macular edema, bilateral",Diabetes mellitus due to underlying condition with moderate nonproliferative diabetic retinopathy with macular edema,9
E08339,3,E083393,"Diabetes with moderate nonp rtnop without macular edema, bi","Diabetes mellitus due to underlying condition with moderate nonproliferative diabetic retinopathy without macular edema, bilateral",Diabetes mellitus due to underlying condition with moderate nonproliferative diabetic retinopathy without macular edema,9
E08341,3,E083413,"Diabetes with severe nonp rtnop with macular edema, bi","Diabetes mellitus due to underlying condition with severe nonproliferative diabetic retinopathy with macular edema, bilateral",Diabetes mellitus due to underlying condition with severe nonproliferative diabetic retinopathy with macular edema,9
E08349,3,E083493,"Diabetes with severe nonp rtnop without macular edema, bi","Diabetes mellitus due to underlying condition with severe nonproliferative diabetic retinopathy without macular edema, bilateral",Diabetes mellitus due to underlying condition with severe nonproliferative diabetic retinopathy without macular edema,9
E08351,3,E083513,"Diabetes with prolif diabetic rtnop with macular edema, bi","Diabetes mellitus due to underlying condition with proliferative diabetic retinopathy with macular edema, bilateral",Diabetes mellitus due to underlying condition with proliferative diabetic retinopathy with macular edema,9
E06,4,E064,Drug-induced thyroiditis,Drug-induced thyroiditis,Thyroiditis,9
E08352,3,E083523,"Diab with prolif diabetic rtnop with trctn dtch macula, bi","Diabetes mellitus due to underlying condition with proliferative diabetic retinopathy with traction retinal detachment involving the macula, bilateral",Diabetes mellitus due to underlying condition with proliferative diabetic retinopathy with traction retinal detachment involving the macula,9
E08353,3,E083533,"Diab with prolif diabetic rtnop with trctn dtch n-mcla, bi","Diabetes mellitus due to underlying condition with proliferative diabetic retinopathy with traction retinal detachment not involving the macula, bilateral",Diabetes mellitus due to underlying condition with proliferative diabetic retinopathy with traction retinal detachment not involving the macula,9
E08354,3,E083543,"Diabetes with prolif diabetic rtnop with combined detach, bi","Diabetes mellitus due to underlying condition with proliferative diabetic retinopathy with combined traction retinal detachment and rhegmatogenous retinal detachment, bilateral",Diabetes mellitus due to underlying condition with proliferative diabetic retinopathy with combined traction retinal detachment and rhegmatogenous retinal detachment,9
E08355,3,E083553,"Diabetes with stable prolif diabetic retinopathy, bilateral","Diabetes mellitus due to underlying condition with stable proliferative diabetic retinopathy, bilateral",Diabetes mellitus due to underlying condition with stable proliferative diabetic retinopathy,9
E08359,3,E083593,"Diab with prolif diabetic rtnop without macular edema, bi","Diabetes mellitus due to underlying condition with proliferative diabetic retinopathy without macular edema, bilateral",Diabetes mellitus due to underlying condition with proliferative diabetic retinopathy without macular edema,9
E084,3,E0843,Diab due to undrl cond w diabetic autonm (poly)neuropathy,Diabetes mellitus due to underlying condition with diabetic autonomic (poly)neuropathy,Diabetes mellitus due to underlying condition with neurological complications,9
E09321,3,E093213,"Drug/chem diab with mild nonp rtnop with macular edema, bi","Drug or chemical induced diabetes mellitus with mild nonproliferative diabetic retinopathy with macular edema, bilateral",Drug or chemical induced diabetes mellitus with mild nonproliferative diabetic retinopathy with macular edema,9
E09329,3,E093293,"Drug/chem diab with mild nonp rtnop without mclr edema, bi","Drug or chemical induced diabetes mellitus with mild nonproliferative diabetic retinopathy without macular edema, bilateral",Drug or chemical induced diabetes mellitus with mild nonproliferative diabetic retinopathy without macular edema,9
E09331,3,E093313,"Drug/chem diab with mod nonp rtnop with macular edema, bi","Drug or chemical induced diabetes mellitus with moderate nonproliferative diabetic retinopathy with macular edema, bilateral",Drug or chemical induced diabetes mellitus with moderate nonproliferative diabetic retinopathy with macular edema,9
E09339,3,E093393,"Drug/chem diab with mod nonp rtnop without macular edema, bi","Drug or chemical induced diabetes mellitus with moderate nonproliferative diabetic retinopathy without macular edema, bilateral",Drug or chemical induced diabetes mellitus with moderate nonproliferative diabetic retinopathy without macular edema,9
E09341,3,E093413,"Drug/chem diab with severe nonp rtnop with macular edema, bi","Drug or chemical induced diabetes mellitus with severe nonproliferative diabetic retinopathy with macular edema, bilateral",Drug or chemical induced diabetes mellitus with severe nonproliferative diabetic retinopathy with macular edema,9
E09349,3,E093493,"Drug/chem diab with severe nonp rtnop without mclr edema, bi","Drug or chemical induced diabetes mellitus with severe nonproliferative diabetic retinopathy without macular edema, bilateral",Drug or chemical induced diabetes mellitus with severe nonproliferative diabetic retinopathy without macular edema,9
E09351,3,E093513,"Drug/chem diab with prolif diab rtnop with macular edema, bi","Drug or chemical induced diabetes mellitus with proliferative diabetic retinopathy with macular edema, bilateral",Drug or chemical induced diabetes mellitus with proliferative diabetic retinopathy with macular edema,9
E09352,3,E093523,"Drug/chem diab w prolif diab rtnop w trctn dtch macula, bi","Drug or chemical induced diabetes mellitus with proliferative diabetic retinopathy with traction retinal detachment involving the macula, bilateral",Drug or chemical induced diabetes mellitus with proliferative diabetic retinopathy with traction retinal detachment involving the macula,9
E09353,3,E093533,"Drug/chem diab w prolif diab rtnop w trctn dtch n-mcla, bi","Drug or chemical induced diabetes mellitus with proliferative diabetic retinopathy with traction retinal detachment not involving the macula, bilateral",Drug or chemical induced diabetes mellitus with proliferative diabetic retinopathy with traction retinal detachment not involving the macula,9
E09354,3,E093543,"Drug/chem diab with prolif diab rtnop with comb detach, bi","Drug or chemical induced diabetes mellitus with proliferative diabetic retinopathy with combined traction retinal detachment and rhegmatogenous retinal detachment, bilateral",Drug or chemical induced diabetes mellitus with proliferative diabetic retinopathy with combined traction retinal detachment and rhegmatogenous retinal detachment,9
E09355,3,E093553,"Drug/chem diabetes with stable prolif diabetic rtnop, bi","Drug or chemical induced diabetes mellitus with stable proliferative diabetic retinopathy, bilateral",Drug or chemical induced diabetes mellitus with stable proliferative diabetic retinopathy,9
E09359,3,E093593,"Drug/chem diab with prolif diab rtnop without mclr edema, bi","Drug or chemical induced diabetes mellitus with proliferative diabetic retinopathy without macular edema, bilateral",Drug or chemical induced diabetes mellitus with proliferative diabetic retinopathy without macular edema,9
E094,3,E0943,Drug/chem diab w neuro comp w diab autonm (poly)neuropathy,Drug or chemical induced diabetes mellitus with neurological complications with diabetic autonomic (poly)neuropathy,Drug or chemical induced diabetes mellitus with neurological complications,9
E10321,3,E103213,"Type 1 diabetes with mild nonp rtnop with macular edema, bi","Type 1 diabetes mellitus with mild nonproliferative diabetic retinopathy with macular edema, bilateral",Type 1 diabetes mellitus with mild nonproliferative diabetic retinopathy with macular edema,9
E10329,3,E103293,"Type 1 diab with mild nonp rtnop without macular edema, bi","Type 1 diabetes mellitus with mild nonproliferative diabetic retinopathy without macular edema, bilateral",Type 1 diabetes mellitus with mild nonproliferative diabetic retinopathy without macular edema,9
E10331,3,E103313,"Type 1 diab with moderate nonp rtnop with macular edema, bi","Type 1 diabetes mellitus with moderate nonproliferative diabetic retinopathy with macular edema, bilateral",Type 1 diabetes mellitus with moderate nonproliferative diabetic retinopathy with macular edema,9
F1698,3,F16983,"Hallucign use, unsp w hallucign persist perception disorder","Hallucinogen use, unspecified with hallucinogen persisting perception disorder (flashbacks)","Hallucinogen use, unspecified with other specified hallucinogen-induced disorder",9
E10339,3,E103393,"Type 1 diab with mod nonp rtnop without macular edema, bi","Type 1 diabetes mellitus with moderate nonproliferative diabetic retinopathy without macular edema, bilateral",Type 1 diabetes mellitus with moderate nonproliferative diabetic retinopathy without macular edema,9
E10341,3,E103413,"Type 1 diab with severe nonp rtnop with macular edema, bi","Type 1 diabetes mellitus with severe nonproliferative diabetic retinopathy with macular edema, bilateral",Type 1 diabetes mellitus with severe nonproliferative diabetic retinopathy with macular edema,9
E10349,3,E103493,"Type 1 diab with severe nonp rtnop without macular edema, bi","Type 1 diabetes mellitus with severe nonproliferative diabetic retinopathy without macular edema, bilateral",Type 1 diabetes mellitus with severe nonproliferative diabetic retinopathy without macular edema,9
E10351,3,E103513,"Type 1 diab with prolif diab rtnop with macular edema, bi","Type 1 diabetes mellitus with proliferative diabetic retinopathy with macular edema, bilateral",Type 1 diabetes mellitus with proliferative diabetic retinopathy with macular edema,9
E10352,3,E103523,"Type 1 diab w prolif diab rtnop with trctn dtch macula, bi","Type 1 diabetes mellitus with proliferative diabetic retinopathy with traction retinal detachment involving the macula, bilateral",Type 1 diabetes mellitus with proliferative diabetic retinopathy with traction retinal detachment involving the macula,9
E10353,3,E103533,"Type 1 diab w prolif diab rtnop with trctn dtch n-mcla, bi","Type 1 diabetes mellitus with proliferative diabetic retinopathy with traction retinal detachment not involving the macula, bilateral",Type 1 diabetes mellitus with proliferative diabetic retinopathy with traction retinal detachment not involving the macula,9
E10354,3,E103543,"Type 1 diab with prolif diabetic rtnop with comb detach, bi","Type 1 diabetes mellitus with proliferative diabetic retinopathy with combined traction retinal detachment and rhegmatogenous retinal detachment, bilateral",Type 1 diabetes mellitus with proliferative diabetic retinopathy with combined traction retinal detachment and rhegmatogenous retinal detachment,9
E10355,3,E103553,"Type 1 diabetes with stable prolif diabetic rtnop, bilateral","Type 1 diabetes mellitus with stable proliferative diabetic retinopathy, bilateral",Type 1 diabetes mellitus with stable proliferative diabetic retinopathy,9
E10359,3,E103593,"Type 1 diab with prolif diab rtnop without macular edema, bi","Type 1 diabetes mellitus with proliferative diabetic retinopathy without macular edema, bilateral",Type 1 diabetes mellitus with proliferative diabetic retinopathy without macular edema,9
E104,3,E1043,Type 1 diabetes w diabetic autonomic (poly)neuropathy,Type 1 diabetes mellitus with diabetic autonomic (poly)neuropathy,Type 1 diabetes mellitus with neurological complications,9
E11321,3,E113213,"Type 2 diabetes with mild nonp rtnop with macular edema, bi","Type 2 diabetes mellitus with mild nonproliferative diabetic retinopathy with macular edema, bilateral",Type 2 diabetes mellitus with mild nonproliferative diabetic retinopathy with macular edema,9
E11329,3,E113293,"Type 2 diab with mild nonp rtnop without macular edema, bi","Type 2 diabetes mellitus with mild nonproliferative diabetic retinopathy without macular edema, bilateral",Type 2 diabetes mellitus with mild nonproliferative diabetic retinopathy without macular edema,9
E11331,3,E113313,"Type 2 diab with moderate nonp rtnop with macular edema, bi","Type 2 diabetes mellitus with moderate nonproliferative diabetic retinopathy with macular edema, bilateral",Type 2 diabetes mellitus with moderate nonproliferative diabetic retinopathy with macular edema,9
E11339,3,E113393,"Type 2 diab with mod nonp rtnop without macular edema, bi","Type 2 diabetes mellitus with moderate nonproliferative diabetic retinopathy without macular edema, bilateral",Type 2 diabetes mellitus with moderate nonproliferative diabetic retinopathy without macular edema,9
E11341,3,E113413,"Type 2 diab with severe nonp rtnop with macular edema, bi","Type 2 diabetes mellitus with severe nonproliferative diabetic retinopathy with macular edema, bilateral",Type 2 diabetes mellitus with severe nonproliferative diabetic retinopathy with macular edema,9
E11349,3,E113493,"Type 2 diab with severe nonp rtnop without macular edema, bi","Type 2 diabetes mellitus with severe nonproliferative diabetic retinopathy without macular edema, bilateral",Type 2 diabetes mellitus with severe nonproliferative diabetic retinopathy without macular edema,9
E11351,3,E113513,"Type 2 diab with prolif diab rtnop with macular edema, bi","Type 2 diabetes mellitus with proliferative diabetic retinopathy with macular edema, bilateral",Type 2 diabetes mellitus with proliferative diabetic retinopathy with macular edema,9
E11352,3,E113523,"Type 2 diab w prolif diab rtnop with trctn dtch macula, bi","Type 2 diabetes mellitus with proliferative diabetic retinopathy with traction retinal detachment involving the macula, bilateral",Type 2 diabetes mellitus with proliferative diabetic retinopathy with traction retinal detachment involving the macula,9
E11353,3,E113533,"Type 2 diab w prolif diab rtnop with trctn dtch n-mcla, bi","Type 2 diabetes mellitus with proliferative diabetic retinopathy with traction retinal detachment not involving the macula, bilateral",Type 2 diabetes mellitus with proliferative diabetic retinopathy with traction retinal detachment not involving the macula,9
E11354,3,E113543,"Type 2 diab with prolif diabetic rtnop with comb detach, bi","Type 2 diabetes mellitus with proliferative diabetic retinopathy with combined traction retinal detachment and rhegmatogenous retinal detachment, bilateral",Type 2 diabetes mellitus with proliferative diabetic retinopathy with combined traction retinal detachment and rhegmatogenous retinal detachment,9
E11355,3,E113553,"Type 2 diabetes with stable prolif diabetic rtnop, bilateral","Type 2 diabetes mellitus with stable proliferative diabetic retinopathy, bilateral",Type 2 diabetes mellitus with stable proliferative diabetic retinopathy,9
E11359,3,E113593,"Type 2 diab with prolif diab rtnop without macular edema, bi","Type 2 diabetes mellitus with proliferative diabetic retinopathy without macular edema, bilateral",Type 2 diabetes mellitus with proliferative diabetic retinopathy without macular edema,9
E114,3,E1143,Type 2 diabetes w diabetic autonomic (poly)neuropathy,Type 2 diabetes mellitus with diabetic autonomic (poly)neuropathy,Type 2 diabetes mellitus with neurological complications,9
E13321,3,E133213,"Oth diabetes with mild nonp rtnop with macular edema, bi","Other specified diabetes mellitus with mild nonproliferative diabetic retinopathy with macular edema, bilateral",Other specified diabetes mellitus with mild nonproliferative diabetic retinopathy with macular edema,9
E13329,3,E133293,"Oth diabetes with mild nonp rtnop without macular edema, bi","Other specified diabetes mellitus with mild nonproliferative diabetic retinopathy without macular edema, bilateral",Other specified diabetes mellitus with mild nonproliferative diabetic retinopathy without macular edema,9
E13331,3,E133313,"Oth diabetes with moderate nonp rtnop with macular edema, bi","Other specified diabetes mellitus with moderate nonproliferative diabetic retinopathy with macular edema, bilateral",Other specified diabetes mellitus with moderate nonproliferative diabetic retinopathy with macular edema,9
E13339,3,E133393,"Oth diab with moderate nonp rtnop without macular edema, bi","Other specified diabetes mellitus with moderate nonproliferative diabetic retinopathy without macular edema, bilateral",Other specified diabetes mellitus with moderate nonproliferative diabetic retinopathy without macular edema,9
E13341,3,E133413,"Oth diabetes with severe nonp rtnop with macular edema, bi","Other specified diabetes mellitus with severe nonproliferative diabetic retinopathy with macular edema, bilateral",Other specified diabetes mellitus with severe nonproliferative diabetic retinopathy with macular edema,9
E13349,3,E133493,"Oth diab with severe nonp rtnop without macular edema, bi","Other specified diabetes mellitus with severe nonproliferative diabetic retinopathy without macular edema, bilateral",Other specified diabetes mellitus with severe nonproliferative diabetic retinopathy without macular edema,9
E13351,3,E133513,"Oth diab with prolif diabetic rtnop with macular edema, bi","Other specified diabetes mellitus with proliferative diabetic retinopathy with macular edema, bilateral",Other specified diabetes mellitus with proliferative diabetic retinopathy with macular edema,9
E13352,3,E133523,"Oth diab with prolif diab rtnop with trctn dtch macula, bi","Other specified diabetes mellitus with proliferative diabetic retinopathy with traction retinal detachment involving the macula, bilateral",Other specified diabetes mellitus with proliferative diabetic retinopathy with traction retinal detachment involving the macula,9
E13353,3,E133533,"Oth diab with prolif diab rtnop with trctn dtch n-mcla, bi","Other specified diabetes mellitus with proliferative diabetic retinopathy with traction retinal detachment not involving the macula, bilateral",Other specified diabetes mellitus with proliferative diabetic retinopathy with traction retinal detachment not involving the macula,9
E13354,3,E133543,"Oth diabetes with prolif diabetic rtnop with comb detach, bi","Other specified diabetes mellitus with proliferative diabetic retinopathy with combined traction retinal detachment and rhegmatogenous retinal detachment, bilateral",Other specified diabetes mellitus with proliferative diabetic retinopathy with combined traction retinal detachment and rhegmatogenous retinal detachment,9
E13355,3,E133553,"Oth diabetes with stable prolif diabetic rtnop, bilateral","Other specified diabetes mellitus with stable proliferative diabetic retinopathy, bilateral",Other specified diabetes mellitus with stable proliferative diabetic retinopathy,9
E13359,3,E133593,"Oth diab with prolif diab rtnop without macular edema, bi","Other specified diabetes mellitus with proliferative diabetic retinopathy without macular edema, bilateral",Other specified diabetes mellitus with proliferative diabetic retinopathy without macular edema,9
E134,3,E1343,Oth diabetes mellitus w diabetic autonomic (poly)neuropathy,Other specified diabetes mellitus with diabetic autonomic (poly)neuropathy,Other specified diabetes mellitus with neurological complications,9
E16,3,E163,Increased secretion of glucagon,Increased secretion of glucagon,Other disorders of pancreatic internal secretion,9
E21,3,E213,"Hyperparathyroidism, unspecified","Hyperparathyroidism, unspecified",Hyperparathyroidism and other disorders of parathyroid gland,9
E23,3,E233,"Hypothalamic dysfunction, not elsewhere classified","Hypothalamic dysfunction, not elsewhere classified",Hypofunction and other disorders of the pituitary gland,9
E24,3,E243,Ectopic ACTH syndrome,Ectopic ACTH syndrome,Cushing's syndrome,9
E27,3,E273,Drug-induced adrenocortical insufficiency,Drug-induced adrenocortical insufficiency,Other disorders of adrenal gland,9
E312,3,E3123,Multiple endocrine neoplasia [MEN] type IIB,Multiple endocrine neoplasia [MEN] type IIB,Multiple endocrine neoplasia [MEN] syndromes,9
E34,3,E343,Short stature due to endocrine disorder,Short stature due to endocrine disorder,Other endocrine disorders,9
E50,3,E503,Vitamin A deficiency with corneal ulceration and xerosis,Vitamin A deficiency with corneal ulceration and xerosis,Vitamin A deficiency,9
E61,3,E613,Manganese deficiency,Manganese deficiency,Deficiency of other nutrient elements,9
E64,3,E643,Sequelae of rickets,Sequelae of rickets,Sequelae of malnutrition and other nutritional deficiencies,9
E67,3,E673,Hypervitaminosis D,Hypervitaminosis D,Other hyperalimentation,9
E7131,3,E71313,Glutaric aciduria type II,Glutaric aciduria type II,Disorders of fatty-acid oxidation,9
E714,3,E7143,Iatrogenic carnitine deficiency,Iatrogenic carnitine deficiency,Disorders of carnitine metabolism,9
E720,3,E7203,Lowe's syndrome,Lowe's syndrome,Disorders of amino-acid transport,9
E722,3,E7223,Citrullinemia,Citrullinemia,Disorders of urea cycle metabolism,9
E725,3,E7253,Hyperoxaluria,Hyperoxaluria,Disorders of glycine metabolism,9
E740,3,E7403,Cori disease,Cori disease,Glycogen storage disease,9
E752,3,E7523,Krabbe disease,Krabbe disease,Other sphingolipidosis,9
E7524,3,E75243,Niemann-Pick disease type D,Niemann-Pick disease type D,Niemann-Pick disease,9
E760,3,E7603,Scheie's syndrome,Scheie's syndrome,"Mucopolysaccharidosis, type I",9
E85,3,E853,Secondary systemic amyloidosis,Secondary systemic amyloidosis,Amyloidosis,9
E87,3,E873,Alkalosis,Alkalosis,"Other disorders of fluid, electrolyte and acid-base balance",9
E89,3,E893,Postprocedural hypopituitarism,Postprocedural hypopituitarism,"Postprocedural endocrine and metabolic complications and disorders, not elsewhere classified",9
E8982,3,E89823,Postproc seroma of an endo sys org following other procedure,Postprocedural seroma of an endocrine system organ or structure following other procedure,Postprocedural hematoma and seroma of an endocrine system organ or structure,9
F063,3,F0633,Mood disorder due to known physiol cond w manic features,Mood disorder due to known physiological condition with manic features,Mood disorder due to known physiological condition,9
F1618,3,F16183,Hallucign abuse w hallucign persisting perception disorder,Hallucinogen abuse with hallucinogen persisting perception disorder (flashbacks),Hallucinogen abuse with other hallucinogen-induced disorder,9
F1628,3,F16283,Hallucign depend w hallucign persisting perception disorder,Hallucinogen dependence with hallucinogen persisting perception disorder (flashbacks),Hallucinogen dependence with other hallucinogen-induced disorder,9
F1720,3,F17203,"Nicotine dependence unspecified, with withdrawal","Nicotine dependence unspecified, with withdrawal","Nicotine dependence, unspecified",9
F1721,3,F17213,"Nicotine dependence, cigarettes, with withdrawal","Nicotine dependence, cigarettes, with withdrawal","Nicotine dependence, cigarettes",9
F1722,3,F17223,"Nicotine dependence, chewing tobacco, with withdrawal","Nicotine dependence, chewing tobacco, with withdrawal","Nicotine dependence, chewing tobacco",9
F1729,3,F17293,"Nicotine dependence, other tobacco product, with withdrawal","Nicotine dependence, other tobacco product, with withdrawal","Nicotine dependence, other tobacco product",9
F20,3,F203,Undifferentiated schizophrenia,Undifferentiated schizophrenia,Schizophrenia,9
F301,3,F3013,"Manic episode, severe, without psychotic symptoms","Manic episode, severe, without psychotic symptoms",Manic episode without psychotic symptoms,9
F311,3,F3113,"Bipolar disord, crnt epsd manic w/o psych features, severe","Bipolar disorder, current episode manic without psychotic features, severe","Bipolar disorder, current episode manic without psychotic features",9
F316,3,F3163,"Bipolar disord, crnt epsd mixed, severe, w/o psych features","Bipolar disorder, current episode mixed, severe, without psychotic features","Bipolar disorder, current episode mixed",9
F317,3,F3173,"Bipolar disord, in partial remis, most recent episode manic","Bipolar disorder, in partial remission, most recent episode manic","Bipolar disorder, currently in remission",9
F32,3,F323,"Major depressv disord, single epsd, severe w psych features","Major depressive disorder, single episode, severe with psychotic features","Major depressive disorder, single episode",9
F33,3,F333,"Major depressv disorder, recurrent, severe w psych symptoms","Major depressive disorder, recurrent, severe with psychotic symptoms","Major depressive disorder, recurrent",9
F4023,3,F40233,Fear of injury,Fear of injury,"Blood, injection, injury type phobia",9
F4024,3,F40243,Fear of flying,Fear of flying,Situational type phobia,9
F41,3,F413,Other mixed anxiety disorders,Other mixed anxiety disorders,Other anxiety disorders,9
F42,3,F423,Hoarding disorder,Hoarding disorder,Obsessive-compulsive disorder,9
F432,3,F4323,Adjustment disorder with mixed anxiety and depressed mood,Adjustment disorder with mixed anxiety and depressed mood,Adjustment disorders,9
F510,3,F5103,Paradoxical insomnia,Paradoxical insomnia,Insomnia not due to a substance or known physiological condition,9
F511,3,F5113,Hypersomnia due to other mental disorder,Hypersomnia due to other mental disorder,Hypersomnia not due to a substance or known physiological condition,9
F55,3,F553,Abuse of steroids or hormones,Abuse of steroids or hormones,Abuse of non-psychoactive substances,9
F60,3,F603,Borderline personality disorder,Borderline personality disorder,Specific personality disorders,9
F63,3,F633,Trichotillomania,Trichotillomania,Impulse disorders,9
F65,3,F653,Voyeurism,Voyeurism,Paraphilias,9
F681,3,F6813,Factitious disord w comb psych and physcl signs and symptoms,Factitious disorder with combined psychological and physical signs and symptoms,Factitious disorder,9
F84,3,F843,Other childhood disintegrative disorder,Other childhood disintegrative disorder,Pervasive developmental disorders,9
F91,3,F913,Oppositional defiant disorder,Oppositional defiant disorder,Conduct disorders,9
G00,3,G003,Staphylococcal meningitis,Staphylococcal meningitis,"Bacterial meningitis, not elsewhere classified",9
G05,3,G053,Encephalitis and encephalomyelitis in diseases classd elswhr,Encephalitis and encephalomyelitis in diseases classified elsewhere,"Encephalitis, myelitis and encephalomyelitis in diseases classified elsewhere",9
G11,3,G113,Cerebellar ataxia with defective DNA repair,Cerebellar ataxia with defective DNA repair,Hereditary ataxia,9
G122,3,G1223,Primary lateral sclerosis,Primary lateral sclerosis,Motor neuron disease,9
G25,3,G253,Myoclonus,Myoclonus,Other extrapyramidal and movement disorders,9
G258,3,G2583,Benign shuddering attacks,Benign shuddering attacks,Other specified extrapyramidal and movement disorders,9
G318,3,G3183,Dementia with Lewy bodies,Dementia with Lewy bodies,Other specified degenerative diseases of nervous system,9
G37,3,G373,Acute transverse myelitis in demyelinating disease of cnsl,Acute transverse myelitis in demyelinating disease of central nervous system,Other demyelinating diseases of central nervous system,9
G4080,3,G40803,"Other epilepsy, intractable, with status epilepticus","Other epilepsy, intractable, with status epilepticus",Other epilepsy,9
G4081,3,G40813,"Lennox-Gastaut syndrome, intractable, w status epilepticus","Lennox-Gastaut syndrome, intractable, with status epilepticus",Lennox-Gastaut syndrome,9
G4082,3,G40823,"Epileptic spasms, intractable, with status epilepticus","Epileptic spasms, intractable, with status epilepticus",Epileptic spasms,9
G445,3,G4453,Primary thunderclap headache,Primary thunderclap headache,Complicated headache syndromes,9
G448,3,G4483,Primary cough headache,Primary cough headache,Other specified headache syndromes,9
G45,3,G453,Amaurosis fugax,Amaurosis fugax,Transient cerebral ischemic attacks and related syndromes,9
G46,3,G463,Brain stem stroke syndrome,Brain stem stroke syndrome,Vascular syndromes of brain in cerebrovascular diseases,9
G471,3,G4713,Recurrent hypersomnia,Recurrent hypersomnia,Hypersomnia,9
G472,3,G4723,"Circadian rhythm sleep disorder, irregular sleep wake type","Circadian rhythm sleep disorder, irregular sleep wake type",Circadian rhythm sleep disorders,9
G473,3,G4733,Obstructive sleep apnea (adult) (pediatric),Obstructive sleep apnea (adult) (pediatric),Sleep apnea,9
G475,3,G4753,Recurrent isolated sleep paralysis,Recurrent isolated sleep paralysis,Parasomnia,9
G476,3,G4763,Sleep related bruxism,Sleep related bruxism,Sleep related movement disorders,9
G51,3,G513,Clonic hemifacial spasm,Clonic hemifacial spasm,Facial nerve disorders,9
G52,3,G523,Disorders of hypoglossal nerve,Disorders of hypoglossal nerve,Disorders of other cranial nerves,9
G54,3,G543,"Thoracic root disorders, not elsewhere classified","Thoracic root disorders, not elsewhere classified",Nerve root and plexus disorders,9
G560,3,G5603,"Carpal tunnel syndrome, bilateral upper limbs","Carpal tunnel syndrome, bilateral upper limbs",Carpal tunnel syndrome,9
G561,3,G5613,"Other lesions of median nerve, bilateral upper limbs","Other lesions of median nerve, bilateral upper limbs",Other lesions of median nerve,9
G562,3,G5623,"Lesion of ulnar nerve, bilateral upper limbs","Lesion of ulnar nerve, bilateral upper limbs",Lesion of ulnar nerve,9
G563,3,G5633,"Lesion of radial nerve, bilateral upper limbs","Lesion of radial nerve, bilateral upper limbs",Lesion of radial nerve,9
G564,3,G5643,Causalgia of bilateral upper limbs,Causalgia of bilateral upper limbs,Causalgia of upper limb,9
G568,3,G5683,Other specified mononeuropathies of bilateral upper limbs,Other specified mononeuropathies of bilateral upper limbs,Other specified mononeuropathies of upper limb,9
G569,3,G5693,Unspecified mononeuropathy of bilateral upper limbs,Unspecified mononeuropathy of bilateral upper limbs,Unspecified mononeuropathy of upper limb,9
G570,3,G5703,"Lesion of sciatic nerve, bilateral lower limbs","Lesion of sciatic nerve, bilateral lower limbs",Lesion of sciatic nerve,9
G571,3,G5713,"Meralgia paresthetica, bilateral lower limbs","Meralgia paresthetica, bilateral lower limbs",Meralgia paresthetica,9
G572,3,G5723,"Lesion of femoral nerve, bilateral lower limbs","Lesion of femoral nerve, bilateral lower limbs",Lesion of femoral nerve,9
G573,3,G5733,"Lesion of lateral popliteal nerve, bilateral lower limbs","Lesion of lateral popliteal nerve, bilateral lower limbs",Lesion of lateral popliteal nerve,9
G574,3,G5743,"Lesion of medial popliteal nerve, bilateral lower limbs","Lesion of medial popliteal nerve, bilateral lower limbs",Lesion of medial popliteal nerve,9
G575,3,G5753,"Tarsal tunnel syndrome, bilateral lower limbs","Tarsal tunnel syndrome, bilateral lower limbs",Tarsal tunnel syndrome,9
G576,3,G5763,"Lesion of plantar nerve, bilateral lower limbs","Lesion of plantar nerve, bilateral lower limbs",Lesion of plantar nerve,9
G577,3,G5773,Causalgia of bilateral lower limbs,Causalgia of bilateral lower limbs,Causalgia of lower limb,9
A010,4,A0104,Typhoid arthritis,Typhoid arthritis,Typhoid fever,9
A022,4,A0224,Salmonella osteomyelitis,Salmonella osteomyelitis,Localized salmonella infections,9
A04,4,A044,Other intestinal Escherichia coli infections,Other intestinal Escherichia coli infections,Other bacterial intestinal infections,9
A05,4,A054,Foodborne Bacillus cereus intoxication,Foodborne Bacillus cereus intoxication,"Other bacterial foodborne intoxications, not elsewhere classified",9
A06,4,A064,Amebic liver abscess,Amebic liver abscess,Amebiasis,9
A07,4,A074,Cyclosporiasis,Cyclosporiasis,Other protozoal intestinal diseases,9
A15,4,A154,Tuberculosis of intrathoracic lymph nodes,Tuberculosis of intrathoracic lymph nodes,Respiratory tuberculosis,9
A181,4,A1814,Tuberculosis of prostate,Tuberculosis of prostate,Tuberculosis of genitourinary system,9
A185,4,A1854,Tuberculous iridocyclitis,Tuberculous iridocyclitis,Tuberculosis of eye,9
A188,4,A1884,Tuberculosis of heart,Tuberculosis of heart,Tuberculosis of other specified organs,9
A30,4,A304,Borderline lepromatous leprosy,Borderline lepromatous leprosy,Leprosy [Hansen's disease],9
A368,4,A3684,Diphtheritic tubulo-interstitial nephropathy,Diphtheritic tubulo-interstitial nephropathy,Other diphtheria,9
A39,4,A394,"Meningococcemia, unspecified","Meningococcemia, unspecified",Meningococcal infection,9
A398,4,A3984,Postmeningococcal arthritis,Postmeningococcal arthritis,Other meningococcal infections,9
A48,4,A484,Brazilian purpuric fever,Brazilian purpuric fever,"Other bacterial diseases, not elsewhere classified",9
A500,4,A5004,Early congenital syphilitic pneumonia,Early congenital syphilitic pneumonia,"Early congenital syphilis, symptomatic",9
A504,4,A5044,Late congenital syphilitic optic nerve atrophy,Late congenital syphilitic optic nerve atrophy,Late congenital neurosyphilis [juvenile neurosyphilis],9
A505,4,A5054,Late congenital cardiovascular syphilis,Late congenital cardiovascular syphilis,"Other late congenital syphilis, symptomatic",9
A514,4,A5144,Secondary syphilitic nephritis,Secondary syphilitic nephritis,Other secondary syphilis,9
A520,4,A5204,Syphilitic cerebral arteritis,Syphilitic cerebral arteritis,Cardiovascular and cerebrovascular syphilis,9
A521,4,A5214,Late syphilitic encephalitis,Late syphilitic encephalitis,Symptomatic neurosyphilis,9
A527,4,A5274,Syphilis of liver and other viscera,Syphilis of liver and other viscera,Other symptomatic late syphilis,9
A542,4,A5424,Gonococcal female pelvic inflammatory disease,Gonococcal female pelvic inflammatory disease,Gonococcal pelviperitonitis and other gonococcal genitourinary infection,9
A548,4,A5484,Gonococcal pneumonia,Gonococcal pneumonia,Other gonococcal infections,9
A600,4,A6004,Herpesviral vulvovaginitis,Herpesviral vulvovaginitis,Herpesviral infection of genitalia and urogenital tract,9
A66,4,A664,Gummata and ulcers of yaws,Gummata and ulcers of yaws,Yaws,9
A83,4,A834,Australian encephalitis,Australian encephalitis,Mosquito-borne viral encephalitis,9
A98,4,A984,Ebola virus disease,Ebola virus disease,"Other viral hemorrhagic fevers, not elsewhere classified",9
B00,4,B004,Herpesviral encephalitis,Herpesviral encephalitis,Herpesviral [herpes simplex] infections,9
B022,4,B0224,Postherpetic myelitis,Postherpetic myelitis,Zoster with other nervous system involvement,9
B023,4,B0234,Zoster scleritis,Zoster scleritis,Zoster ocular disease,9
B05,4,B054,Measles with intestinal complications,Measles with intestinal complications,Measles,9
B268,4,B2684,Mumps polyneuropathy,Mumps polyneuropathy,Mumps with other complications,9
B332,4,B3324,Viral cardiomyopathy,Viral cardiomyopathy,Viral carditis,9
B34,4,B344,"Papovavirus infection, unspecified","Papovavirus infection, unspecified",Viral infection of unspecified site,9
B35,4,B354,Tinea corporis,Tinea corporis,Dermatophytosis,9
B378,4,B3784,Candidal otitis externa,Candidal otitis externa,Candidiasis of other sites,9
B38,4,B384,Coccidioidomycosis meningitis,Coccidioidomycosis meningitis,Coccidioidomycosis,9
B39,4,B394,"Histoplasmosis capsulati, unspecified","Histoplasmosis capsulati, unspecified",Histoplasmosis,9
B46,4,B464,Disseminated mucormycosis,Disseminated mucormycosis,Zygomycosis,9
B81,4,B814,Mixed intestinal helminthiases,Mixed intestinal helminthiases,"Other intestinal helminthiases, not elsewhere classified",9
B83,4,B834,Internal hirudiniasis,Internal hirudiniasis,Other helminthiases,9
B85,4,B854,Mixed pediculosis and phthiriasis,Mixed pediculosis and phthiriasis,Pediculosis and phthiriasis,9
B87,4,B874,Aural myiasis,Aural myiasis,Myiasis,9
B95,4,B954,Oth streptococcus as the cause of diseases classd elswhr,Other streptococcus as the cause of diseases classified elsewhere,"Streptococcus, Staphylococcus, and Enterococcus as the cause of diseases classified elsewhere",9
B973,4,B9734,HTLV-II as the cause of diseases classified elsewhere,"Human T-cell lymphotrophic virus, type II [HTLV-II] as the cause of diseases classified elsewhere",Retrovirus as the cause of diseases classified elsewhere,9
C00,4,C004,"Malignant neoplasm of lower lip, inner aspect","Malignant neoplasm of lower lip, inner aspect",Malignant neoplasm of lip,9
C02,4,C024,Malignant neoplasm of lingual tonsil,Malignant neoplasm of lingual tonsil,Malignant neoplasm of other and unspecified parts of tongue,9
C10,4,C104,Malignant neoplasm of branchial cleft,Malignant neoplasm of branchial cleft,Malignant neoplasm of oropharynx,9
C15,4,C154,Malignant neoplasm of middle third of esophagus,Malignant neoplasm of middle third of esophagus,Malignant neoplasm of esophagus,9
C16,4,C164,Malignant neoplasm of pylorus,Malignant neoplasm of pylorus,Malignant neoplasm of stomach,9
C18,4,C184,Malignant neoplasm of transverse colon,Malignant neoplasm of transverse colon,Malignant neoplasm of colon,9
C22,4,C224,Other sarcomas of liver,Other sarcomas of liver,Malignant neoplasm of liver and intrahepatic bile ducts,9
C25,4,C254,Malignant neoplasm of endocrine pancreas,Malignant neoplasm of endocrine pancreas,Malignant neoplasm of pancreas,9
C38,4,C384,Malignant neoplasm of pleura,Malignant neoplasm of pleura,"Malignant neoplasm of heart, mediastinum and pleura",9
C41,4,C414,"Malignant neoplasm of pelvic bones, sacrum and coccyx","Malignant neoplasm of pelvic bones, sacrum and coccyx",Malignant neoplasm of bone and articular cartilage of other and unspecified sites,9
C46,4,C464,Kaposi's sarcoma of gastrointestinal sites,Kaposi's sarcoma of gastrointestinal sites,Kaposi's sarcoma,9
C49A,4,C49A4,Gastrointestinal stromal tumor of large intestine,Gastrointestinal stromal tumor of large intestine,Gastrointestinal stromal tumor,9
C67,4,C674,Malignant neoplasm of posterior wall of bladder,Malignant neoplasm of posterior wall of bladder,Malignant neoplasm of bladder,9
C71,4,C714,Malignant neoplasm of occipital lobe,Malignant neoplasm of occipital lobe,Malignant neoplasm of brain,9
C75,4,C754,Malignant neoplasm of carotid body,Malignant neoplasm of carotid body,Malignant neoplasm of other endocrine glands and related structures,9
C7A02,4,C7A024,Malignant carcinoid tumor of the descending colon,Malignant carcinoid tumor of the descending colon,"Malignant carcinoid tumors of the appendix, large intestine, and rectum",9
C7A09,4,C7A094,"Malignant carcinoid tumor of the foregut, unspecified","Malignant carcinoid tumor of the foregut, unspecified",Malignant carcinoid tumors of other sites,9
C7B0,4,C7B04,Secondary carcinoid tumors of peritoneum,Secondary carcinoid tumors of peritoneum,Secondary carcinoid tumors,9
C77,4,C774,Sec and unsp malig neoplasm of inguinal and lower limb nodes,Secondary and unspecified malignant neoplasm of inguinal and lower limb lymph nodes,Secondary and unspecified malignant neoplasm of lymph nodes,9
C810,4,C8104,"Nodlr lymphocy predom Hdgkn lymph, nodes of axla and upr lmb","Nodular lymphocyte predominant Hodgkin lymphoma, lymph nodes of axilla and upper limb",Nodular lymphocyte predominant Hodgkin lymphoma,9
C811,4,C8114,"Nodular scler Hodgkin lymph, nodes of axilla and upper limb","Nodular sclerosis Hodgkin lymphoma, lymph nodes of axilla and upper limb",Nodular sclerosis Hodgkin lymphoma,9
C812,4,C8124,"Mixed cellular Hodgkin lymph, nodes of axilla and upper limb","Mixed cellularity Hodgkin lymphoma, lymph nodes of axilla and upper limb",Mixed cellularity Hodgkin lymphoma,9
C813,4,C8134,"Lymphocy deplet Hdgkn lymph, nodes of axilla and upper limb","Lymphocyte depleted Hodgkin lymphoma, lymph nodes of axilla and upper limb",Lymphocyte depleted Hodgkin lymphoma,9
C814,4,C8144,"Lymp-rich Hodgkin lymphoma, nodes of axilla and upper limb","Lymphocyte-rich Hodgkin lymphoma, lymph nodes of axilla and upper limb",Lymphocyte-rich Hodgkin lymphoma,9
C817,4,C8174,"Other Hodgkin lymphoma, lymph nodes of axilla and upper limb","Other Hodgkin lymphoma, lymph nodes of axilla and upper limb",Other Hodgkin lymphoma,9
C819,4,C8194,"Hodgkin lymphoma, unsp, lymph nodes of axilla and upper limb","Hodgkin lymphoma, unspecified, lymph nodes of axilla and upper limb","Hodgkin lymphoma, unspecified",9
C820,4,C8204,"Follicular lymphoma grade I, nodes of axilla and upper limb","Follicular lymphoma grade I, lymph nodes of axilla and upper limb",Follicular lymphoma grade I,9
C821,4,C8214,"Follicular lymphoma grade II, nodes of axilla and upper limb","Follicular lymphoma grade II, lymph nodes of axilla and upper limb",Follicular lymphoma grade II,9
C822,4,C8224,"Foliclar lymph grade III, unsp, nodes of axla and upper limb","Follicular lymphoma grade III, unspecified, lymph nodes of axilla and upper limb","Follicular lymphoma grade III, unspecified",9
C823,4,C8234,"Foliclar lymphoma grade IIIa, nodes of axilla and upper limb","Follicular lymphoma grade IIIa, lymph nodes of axilla and upper limb",Follicular lymphoma grade IIIa,9
C824,4,C8244,"Foliclar lymphoma grade IIIb, nodes of axilla and upper limb","Follicular lymphoma grade IIIb, lymph nodes of axilla and upper limb",Follicular lymphoma grade IIIb,9
C825,4,C8254,"Diffuse folicl center lymph, nodes of axilla and upper limb","Diffuse follicle center lymphoma, lymph nodes of axilla and upper limb",Diffuse follicle center lymphoma,9
C826,4,C8264,"Cutan folicl center lymphoma, nodes of axilla and upper limb","Cutaneous follicle center lymphoma, lymph nodes of axilla and upper limb",Cutaneous follicle center lymphoma,9
C828,4,C8284,"Oth types of foliclar lymph, nodes of axilla and upper limb","Other types of follicular lymphoma, lymph nodes of axilla and upper limb",Other types of follicular lymphoma,9
C829,4,C8294,"Follicular lymphoma, unsp, nodes of axilla and upper limb","Follicular lymphoma, unspecified, lymph nodes of axilla and upper limb","Follicular lymphoma, unspecified",9
C830,4,C8304,"Small cell B-cell lymphoma, nodes of axilla and upper limb","Small cell B-cell lymphoma, lymph nodes of axilla and upper limb",Small cell B-cell lymphoma,9
C831,4,C8314,"Mantle cell lymphoma, lymph nodes of axilla and upper limb","Mantle cell lymphoma, lymph nodes of axilla and upper limb",Mantle cell lymphoma,9
C833,4,C8334,"Diffuse large B-cell lymph, nodes of axilla and upper limb","Diffuse large B-cell lymphoma, lymph nodes of axilla and upper limb",Diffuse large B-cell lymphoma,9
C835,4,C8354,"Lymphoblastic lymphoma, nodes of axilla and upper limb","Lymphoblastic (diffuse) lymphoma, lymph nodes of axilla and upper limb",Lymphoblastic (diffuse) lymphoma,9
C837,4,C8374,"Burkitt lymphoma, lymph nodes of axilla and upper limb","Burkitt lymphoma, lymph nodes of axilla and upper limb",Burkitt lymphoma,9
C838,4,C8384,"Oth non-follic lymphoma, nodes of axilla and upper limb","Other non-follicular lymphoma, lymph nodes of axilla and upper limb",Other non-follicular lymphoma,9
C839,4,C8394,"Non-follic lymphoma, unsp, nodes of axilla and upper limb","Non-follicular (diffuse) lymphoma, unspecified, lymph nodes of axilla and upper limb","Non-follicular (diffuse) lymphoma, unspecified",9
C840,4,C8404,"Mycosis fungoides, lymph nodes of axilla and upper limb","Mycosis fungoides, lymph nodes of axilla and upper limb",Mycosis fungoides,9
C841,4,C8414,"Sezary disease, lymph nodes of axilla and upper limb","Sezary disease, lymph nodes of axilla and upper limb",Sezary disease,9
C844,4,C8444,"Prph T-cell lymph, not class, nodes of axilla and upper limb","Peripheral T-cell lymphoma, not classified, lymph nodes of axilla and upper limb","Peripheral T-cell lymphoma, not classified",9
C846,4,C8464,"Anaplstc lg cell lymph, ALK-pos, nodes of axla and upr limb","Anaplastic large cell lymphoma, ALK-positive, lymph nodes of axilla and upper limb","Anaplastic large cell lymphoma, ALK-positive",9
C847,4,C8474,"Anaplstc lg cell lymph, ALK-neg, nodes of axla and upr limb","Anaplastic large cell lymphoma, ALK-negative, lymph nodes of axilla and upper limb","Anaplastic large cell lymphoma, ALK-negative",9
C84A,4,C84A4,"Cutan T-cell lymphoma, unsp, nodes of axilla and upper limb","Cutaneous T-cell lymphoma, unspecified, lymph nodes of axilla and upper limb","Cutaneous T-cell lymphoma, unspecified",9
C84Z,4,C84Z4,"Oth mature T/NK-cell lymph, nodes of axilla and upper limb","Other mature T/NK-cell lymphomas, lymph nodes of axilla and upper limb",Other mature T/NK-cell lymphomas,9
C849,4,C8494,"Mature T/NK-cell lymph, unsp, nodes of axilla and upper limb","Mature T/NK-cell lymphomas, unspecified, lymph nodes of axilla and upper limb","Mature T/NK-cell lymphomas, unspecified",9
C851,4,C8514,"Unsp B-cell lymphoma, lymph nodes of axilla and upper limb","Unspecified B-cell lymphoma, lymph nodes of axilla and upper limb",Unspecified B-cell lymphoma,9
C852,4,C8524,"Mediastnl large B-cell lymph, nodes of axilla and upper limb","Mediastinal (thymic) large B-cell lymphoma, lymph nodes of axilla and upper limb",Mediastinal (thymic) large B-cell lymphoma,9
C858,4,C8584,"Oth types of non-hodg lymph, nodes of axilla and upper limb","Other specified types of non-Hodgkin lymphoma, lymph nodes of axilla and upper limb",Other specified types of non-Hodgkin lymphoma,9
C859,4,C8594,"Non-Hodgkin lymphoma, unsp, nodes of axilla and upper limb","Non-Hodgkin lymphoma, unspecified, lymph nodes of axilla and upper limb","Non-Hodgkin lymphoma, unspecified",9
C86,4,C864,Blastic NK-cell lymphoma,Blastic NK-cell lymphoma,Other specified types of T/NK-cell lymphoma,9
C88,4,C884,Extrnod mrgnl zn B-cell lymph of mucosa-assoc lymphoid tiss,Extranodal marginal zone B-cell lymphoma of mucosa-associated lymphoid tissue [MALT-lymphoma],Malignant immunoproliferative diseases and certain other B-cell lymphomas,9
D000,4,D0004,Carcinoma in situ of soft palate,Carcinoma in situ of soft palate,"Carcinoma in situ of lip, oral cavity and pharynx",9
D12,4,D124,Benign neoplasm of descending colon,Benign neoplasm of descending colon,"Benign neoplasm of colon, rectum, anus and anal canal",9
D172,4,D1724,"Benign lipomatous neoplasm of skin, subcu of left leg",Benign lipomatous neoplasm of skin and subcutaneous tissue of left leg,Benign lipomatous neoplasm of skin and subcutaneous tissue of limb,9
D33,4,D334,Benign neoplasm of spinal cord,Benign neoplasm of spinal cord,Benign neoplasm of brain and other parts of central nervous system,9
D361,4,D3614,Benign neoplm of prph nerves and autonm nrv sys of thorax,Benign neoplasm of peripheral nerves and autonomic nervous system of thorax,Benign neoplasm of peripheral nerves and autonomic nervous system,9
D3A02,4,D3A024,Benign carcinoid tumor of the descending colon,Benign carcinoid tumor of the descending colon,"Benign carcinoid tumors of the appendix, large intestine, and rectum",9
D3A09,4,D3A094,"Benign carcinoid tumor of the foregut, unspecified","Benign carcinoid tumor of the foregut, unspecified",Benign carcinoid tumors of other sites,9
D38,4,D384,Neoplasm of uncertain behavior of thymus,Neoplasm of uncertain behavior of thymus,Neoplasm of uncertain behavior of middle ear and respiratory and intrathoracic organs,9
D43,4,D434,Neoplasm of uncertain behavior of spinal cord,Neoplasm of uncertain behavior of spinal cord,Neoplasm of uncertain behavior of brain and central nervous system,9
D48,4,D484,Neoplasm of uncertain behavior of peritoneum,Neoplasm of uncertain behavior of peritoneum,Neoplasm of uncertain behavior of other and unspecified sites,9
D49,4,D494,Neoplasm of unspecified behavior of bladder,Neoplasm of unspecified behavior of bladder,Neoplasms of unspecified behavior,9
D56,4,D564,Hereditary persistence of fetal hemoglobin [HPFH],Hereditary persistence of fetal hemoglobin [HPFH],Thalassemia,9
D59,4,D594,Other nonautoimmune hemolytic anemias,Other nonautoimmune hemolytic anemias,Acquired hemolytic anemia,9
D64,4,D644,Congenital dyserythropoietic anemia,Congenital dyserythropoietic anemia,Other anemias,9
D70,4,D704,Cyclic neutropenia,Cyclic neutropenia,Neutropenia,9
D7282,4,D72824,Basophilia,Basophilia,Elevated white blood cell count,9
D73,4,D734,Cyst of spleen,Cyst of spleen,Diseases of spleen,9
D783,4,D7834,Postproc seroma of the spleen following other procedure,Postprocedural seroma of the spleen following other procedure,Postprocedural hematoma and seroma of the spleen following a procedure,9
D80,4,D804,Selective deficiency of immunoglobulin M [IgM],Selective deficiency of immunoglobulin M [IgM],Immunodeficiency with predominantly antibody defects,9
D81,4,D814,Nezelof's syndrome,Nezelof's syndrome,Combined immunodeficiencies,9
D82,4,D824,Hyperimmunoglobulin E [IgE] syndrome,Hyperimmunoglobulin E [IgE] syndrome,Immunodeficiency associated with other major defects,9
E084,4,E0844,Diabetes due to underlying condition w diabetic amyotrophy,Diabetes mellitus due to underlying condition with diabetic amyotrophy,Diabetes mellitus due to underlying condition with neurological complications,9
E094,4,E0944,Drug/chem diabetes w neurological comp w diabetic amyotrophy,Drug or chemical induced diabetes mellitus with neurological complications with diabetic amyotrophy,Drug or chemical induced diabetes mellitus with neurological complications,9
E104,4,E1044,Type 1 diabetes mellitus with diabetic amyotrophy,Type 1 diabetes mellitus with diabetic amyotrophy,Type 1 diabetes mellitus with neurological complications,9
E114,4,E1144,Type 2 diabetes mellitus with diabetic amyotrophy,Type 2 diabetes mellitus with diabetic amyotrophy,Type 2 diabetes mellitus with neurological complications,9
E134,4,E1344,Other specified diabetes mellitus with diabetic amyotrophy,Other specified diabetes mellitus with diabetic amyotrophy,Other specified diabetes mellitus with neurological complications,9
E16,4,E164,Increased secretion of gastrin,Increased secretion of gastrin,Other disorders of pancreatic internal secretion,9
E21,4,E214,Other specified disorders of parathyroid gland,Other specified disorders of parathyroid gland,Hyperparathyroidism and other disorders of parathyroid gland,9
E24,4,E244,Alcohol-induced pseudo-Cushing's syndrome,Alcohol-induced pseudo-Cushing's syndrome,Cushing's syndrome,9
E34,4,E344,Constitutional tall stature,Constitutional tall stature,Other endocrine disorders,9
E50,4,E504,Vitamin A deficiency with keratomalacia,Vitamin A deficiency with keratomalacia,Vitamin A deficiency,9
E61,4,E614,Chromium deficiency,Chromium deficiency,Deficiency of other nutrient elements,9
E7131,4,E71314,Muscle carnitine palmitoyltransferase deficiency,Muscle carnitine palmitoyltransferase deficiency,Disorders of fatty-acid oxidation,9
E720,4,E7204,Cystinosis,Cystinosis,Disorders of amino-acid transport,9
E740,4,E7404,McArdle disease,McArdle disease,Glycogen storage disease,9
E85,4,E854,Organ-limited amyloidosis,Organ-limited amyloidosis,Amyloidosis,9
E87,4,E874,Mixed disorder of acid-base balance,Mixed disorder of acid-base balance,"Other disorders of fluid, electrolyte and acid-base balance",9
F063,4,F0634,Mood disorder due to known physiol cond w mixed features,Mood disorder due to known physiological condition with mixed features,Mood disorder due to known physiological condition,9
F316,4,F3164,"Bipolar disord, crnt episode mixed, severe, w psych features","Bipolar disorder, current episode mixed, severe, with psychotic features","Bipolar disorder, current episode mixed",9
F317,4,F3174,"Bipolar disorder, in full remis, most recent episode manic","Bipolar disorder, in full remission, most recent episode manic","Bipolar disorder, currently in remission",9
F32,4,F324,"Major depressv disorder, single episode, in partial remis","Major depressive disorder, single episode, in partial remission","Major depressive disorder, single episode",9
F42,4,F424,Excoriation (skin-picking) disorder,Excoriation (skin-picking) disorder,Obsessive-compulsive disorder,9
F432,4,F4324,Adjustment disorder with disturbance of conduct,Adjustment disorder with disturbance of conduct,Adjustment disorders,9
F44,4,F444,Conversion disorder with motor symptom or deficit,Conversion disorder with motor symptom or deficit,Dissociative and conversion disorders,9
F510,4,F5104,Psychophysiologic insomnia,Psychophysiologic insomnia,Insomnia not due to a substance or known physiological condition,9
F55,4,F554,Abuse of vitamins,Abuse of vitamins,Abuse of non-psychoactive substances,9
F60,4,F604,Histrionic personality disorder,Histrionic personality disorder,Specific personality disorders,9
F65,4,F654,Pedophilia,Pedophilia,Paraphilias,9
F80,4,F804,Speech and language development delay due to hearing loss,Speech and language development delay due to hearing loss,Specific developmental disorders of speech and language,9
G05,4,G054,Myelitis in diseases classified elsewhere,Myelitis in diseases classified elsewhere,"Encephalitis, myelitis and encephalomyelitis in diseases classified elsewhere",9
G11,4,G114,Hereditary spastic paraplegia,Hereditary spastic paraplegia,Hereditary ataxia,9
G122,4,G1224,Familial motor neuron disease,Familial motor neuron disease,Motor neuron disease,9
G25,4,G254,Drug-induced chorea,Drug-induced chorea,Other extrapyramidal and movement disorders,9
G318,4,G3184,"Mild cognitive impairment, so stated","Mild cognitive impairment, so stated",Other specified degenerative diseases of nervous system,9
G37,4,G374,Subacute necrotizing myelitis of central nervous system,Subacute necrotizing myelitis of central nervous system,Other demyelinating diseases of central nervous system,9
G4080,4,G40804,"Other epilepsy, intractable, without status epilepticus","Other epilepsy, intractable, without status epilepticus",Other epilepsy,9
G4081,4,G40814,"Lennox-Gastaut syndrome, intractable, w/o status epilepticus","Lennox-Gastaut syndrome, intractable, without status epilepticus",Lennox-Gastaut syndrome,9
G4082,4,G40824,"Epileptic spasms, intractable, without status epilepticus","Epileptic spasms, intractable, without status epilepticus",Epileptic spasms,9
G448,4,G4484,Primary exertional headache,Primary exertional headache,Other specified headache syndromes,9
G45,4,G454,Transient global amnesia,Transient global amnesia,Transient cerebral ischemic attacks and related syndromes,9
G46,4,G464,Cerebellar stroke syndrome,Cerebellar stroke syndrome,Vascular syndromes of brain in cerebrovascular diseases,9
G471,4,G4714,Hypersomnia due to medical condition,Hypersomnia due to medical condition,Hypersomnia,9
G472,4,G4724,"Circadian rhythm sleep disorder, free running type","Circadian rhythm sleep disorder, free running type",Circadian rhythm sleep disorders,9
G473,4,G4734,Idio sleep related nonobstructive alveolar hypoventilation,Idiopathic sleep related nonobstructive alveolar hypoventilation,Sleep apnea,9
G475,4,G4754,Parasomnia in conditions classified elsewhere,Parasomnia in conditions classified elsewhere,Parasomnia,9
G51,4,G514,Facial myokymia,Facial myokymia,Facial nerve disorders,9
G54,4,G544,"Lumbosacral root disorders, not elsewhere classified","Lumbosacral root disorders, not elsewhere classified",Nerve root and plexus disorders,9
A010,5,A0105,Typhoid osteomyelitis,Typhoid osteomyelitis,Typhoid fever,9
A022,5,A0225,Salmonella pyelonephritis,Salmonella pyelonephritis,Localized salmonella infections,9
A04,5,A045,Campylobacter enteritis,Campylobacter enteritis,Other bacterial intestinal infections,9
A05,5,A055,Foodborne Vibrio vulnificus intoxication,Foodborne Vibrio vulnificus intoxication,"Other bacterial foodborne intoxications, not elsewhere classified",9
A06,5,A065,Amebic lung abscess,Amebic lung abscess,Amebiasis,9
A15,5,A155,"Tuberculosis of larynx, trachea and bronchus","Tuberculosis of larynx, trachea and bronchus",Respiratory tuberculosis,9
A181,5,A1815,Tuberculosis of other male genital organs,Tuberculosis of other male genital organs,Tuberculosis of genitourinary system,9
A188,5,A1885,Tuberculosis of spleen,Tuberculosis of spleen,Tuberculosis of other specified organs,9
A30,5,A305,Lepromatous leprosy,Lepromatous leprosy,Leprosy [Hansen's disease],9
A368,5,A3685,Diphtheritic cystitis,Diphtheritic cystitis,Other diphtheria,9
A500,5,A5005,Early congenital syphilitic rhinitis,Early congenital syphilitic rhinitis,"Early congenital syphilis, symptomatic",9
A504,5,A5045,Juvenile general paresis,Juvenile general paresis,Late congenital neurosyphilis [juvenile neurosyphilis],9
A505,5,A5055,Late congenital syphilitic arthropathy,Late congenital syphilitic arthropathy,"Other late congenital syphilis, symptomatic",9
A514,5,A5145,Secondary syphilitic hepatitis,Secondary syphilitic hepatitis,Other secondary syphilis,9
A520,5,A5205,Other cerebrovascular syphilis,Other cerebrovascular syphilis,Cardiovascular and cerebrovascular syphilis,9
A521,5,A5215,Late syphilitic neuropathy,Late syphilitic neuropathy,Symptomatic neurosyphilis,9
A527,5,A5275,Syphilis of kidney and ureter,Syphilis of kidney and ureter,Other symptomatic late syphilis,9
A548,5,A5485,Gonococcal peritonitis,Gonococcal peritonitis,Other gonococcal infections,9
A66,5,A665,Gangosa,Gangosa,Yaws,9
A83,5,A835,California encephalitis,California encephalitis,Mosquito-borne viral encephalitis,9
A98,5,A985,Hemorrhagic fever with renal syndrome,Hemorrhagic fever with renal syndrome,"Other viral hemorrhagic fevers, not elsewhere classified",9
B268,5,B2685,Mumps arthritis,Mumps arthritis,Mumps with other complications,9
B35,5,B355,Tinea imbricata,Tinea imbricata,Dermatophytosis,9
B39,5,B395,Histoplasmosis duboisii,Histoplasmosis duboisii,Histoplasmosis,9
B46,5,B465,"Mucormycosis, unspecified","Mucormycosis, unspecified",Zygomycosis,9
B66,5,B665,Fasciolopsiasis,Fasciolopsiasis,Other fluke infections,9
B95,5,B955,Unsp streptococcus as the cause of diseases classd elswhr,Unspecified streptococcus as the cause of diseases classified elsewhere,"Streptococcus, Staphylococcus, and Enterococcus as the cause of diseases classified elsewhere",9
B973,5,B9735,HIV 2 as the cause of diseases classified elsewhere,"Human immunodeficiency virus, type 2 [HIV 2] as the cause of diseases classified elsewhere",Retrovirus as the cause of diseases classified elsewhere,9
C00,5,C005,"Malignant neoplasm of lip, unspecified, inner aspect","Malignant neoplasm of lip, unspecified, inner aspect",Malignant neoplasm of lip,9
C15,5,C155,Malignant neoplasm of lower third of esophagus,Malignant neoplasm of lower third of esophagus,Malignant neoplasm of esophagus,9
C16,5,C165,"Malignant neoplasm of lesser curvature of stomach, unsp","Malignant neoplasm of lesser curvature of stomach, unspecified",Malignant neoplasm of stomach,9
C18,5,C185,Malignant neoplasm of splenic flexure,Malignant neoplasm of splenic flexure,Malignant neoplasm of colon,9
C49A,5,C49A5,Gastrointestinal stromal tumor of rectum,Gastrointestinal stromal tumor of rectum,Gastrointestinal stromal tumor,9
C67,5,C675,Malignant neoplasm of bladder neck,Malignant neoplasm of bladder neck,Malignant neoplasm of bladder,9
C71,5,C715,Malignant neoplasm of cerebral ventricle,Malignant neoplasm of cerebral ventricle,Malignant neoplasm of brain,9
C75,5,C755,Malignant neoplasm of aortic body and other paraganglia,Malignant neoplasm of aortic body and other paraganglia,Malignant neoplasm of other endocrine glands and related structures,9
C7A02,5,C7A025,Malignant carcinoid tumor of the sigmoid colon,Malignant carcinoid tumor of the sigmoid colon,"Malignant carcinoid tumors of the appendix, large intestine, and rectum",9
C7A09,5,C7A095,"Malignant carcinoid tumor of the midgut, unspecified","Malignant carcinoid tumor of the midgut, unspecified",Malignant carcinoid tumors of other sites,9
C77,5,C775,Secondary and unsp malignant neoplasm of intrapelv nodes,Secondary and unspecified malignant neoplasm of intrapelvic lymph nodes,Secondary and unspecified malignant neoplasm of lymph nodes,9
C810,5,C8105,"Nodlr lymphocy predom Hdgkn lymph,nodes of ing rgn & low lmb","Nodular lymphocyte predominant Hodgkin lymphoma, lymph nodes of inguinal region and lower limb",Nodular lymphocyte predominant Hodgkin lymphoma,9
C811,5,C8115,"Nodlr scler Hdgkn lymph, nodes of ing region and lower limb","Nodular sclerosis Hodgkin lymphoma, lymph nodes of inguinal region and lower limb",Nodular sclerosis Hodgkin lymphoma,9
C812,5,C8125,"Mixed cellular Hdgkn lymph, nodes of ing rgn and lower limb","Mixed cellularity Hodgkin lymphoma, lymph nodes of inguinal region and lower limb",Mixed cellularity Hodgkin lymphoma,9
C813,5,C8135,"Lymphocy deplet Hdgkn lymph, nodes of ing rgn and lower limb","Lymphocyte depleted Hodgkin lymphoma, lymph nodes of inguinal region and lower limb",Lymphocyte depleted Hodgkin lymphoma,9
C814,5,C8145,"Lymp-rich Hodgkin lymph, nodes of ing region and lower limb","Lymphocyte-rich Hodgkin lymphoma, lymph nodes of inguinal region and lower limb",Lymphocyte-rich Hodgkin lymphoma,9
C817,5,C8175,"Other Hodgkin lymphoma, nodes of ing region and lower limb","Other Hodgkin lymphoma, lymph nodes of inguinal region and lower limb",Other Hodgkin lymphoma,9
C819,5,C8195,"Hodgkin lymphoma, unsp, nodes of ing region and lower limb","Hodgkin lymphoma, unspecified, lymph nodes of inguinal region and lower limb","Hodgkin lymphoma, unspecified",9
C820,5,C8205,"Foliclar lymph grade I, nodes of ing region and lower limb","Follicular lymphoma grade I, lymph nodes of inguinal region and lower limb",Follicular lymphoma grade I,9
C821,5,C8215,"Foliclar lymph grade II, nodes of ing region and lower limb","Follicular lymphoma grade II, lymph nodes of inguinal region and lower limb",Follicular lymphoma grade II,9
C822,5,C8225,"Foliclar lymph grade III, unsp, nodes of ing rgn and low lmb","Follicular lymphoma grade III, unspecified, lymph nodes of inguinal region and lower limb","Follicular lymphoma grade III, unspecified",9
C823,5,C8235,"Foliclar lymph grade IIIa, nodes of ing rgn and lower limb","Follicular lymphoma grade IIIa, lymph nodes of inguinal region and lower limb",Follicular lymphoma grade IIIa,9
C824,5,C8245,"Foliclar lymph grade IIIb, nodes of ing rgn and lower limb","Follicular lymphoma grade IIIb, lymph nodes of inguinal region and lower limb",Follicular lymphoma grade IIIb,9
C825,5,C8255,"Diffus folicl cntr lymph, nodes of ing region and lower limb","Diffuse follicle center lymphoma, lymph nodes of inguinal region and lower limb",Diffuse follicle center lymphoma,9
C826,5,C8265,"Cutan folicl cntr lymph, nodes of ing region and lower limb","Cutaneous follicle center lymphoma, lymph nodes of inguinal region and lower limb",Cutaneous follicle center lymphoma,9
C828,5,C8285,"Oth types of foliclar lymph, nodes of ing rgn and lower limb","Other types of follicular lymphoma, lymph nodes of inguinal region and lower limb",Other types of follicular lymphoma,9
C829,5,C8295,"Foliclar lymphoma, unsp, nodes of ing region and lower limb","Follicular lymphoma, unspecified, lymph nodes of inguinal region and lower limb","Follicular lymphoma, unspecified",9
C830,5,C8305,"Small cell B-cell lymph, nodes of ing region and lower limb","Small cell B-cell lymphoma, lymph nodes of inguinal region and lower limb",Small cell B-cell lymphoma,9
C831,5,C8315,"Mantle cell lymphoma, nodes of ing region and lower limb","Mantle cell lymphoma, lymph nodes of inguinal region and lower limb",Mantle cell lymphoma,9
C833,5,C8335,"Diffus large B-cell lymph, nodes of ing rgn and lower limb","Diffuse large B-cell lymphoma, lymph nodes of inguinal region and lower limb",Diffuse large B-cell lymphoma,9
C835,5,C8355,"Lymphoblastic lymphoma, nodes of ing region and lower limb","Lymphoblastic (diffuse) lymphoma, lymph nodes of inguinal region and lower limb",Lymphoblastic (diffuse) lymphoma,9
C837,5,C8375,"Burkitt lymphoma, nodes of inguinal region and lower limb","Burkitt lymphoma, lymph nodes of inguinal region and lower limb",Burkitt lymphoma,9
C838,5,C8385,"Oth non-follic lymphoma, nodes of ing region and lower limb","Other non-follicular lymphoma, lymph nodes of inguinal region and lower limb",Other non-follicular lymphoma,9
C839,5,C8395,"Non-follic lymph, unsp, nodes of ing region and lower limb","Non-follicular (diffuse) lymphoma, unspecified, lymph nodes of inguinal region and lower limb","Non-follicular (diffuse) lymphoma, unspecified",9
C840,5,C8405,"Mycosis fungoides, nodes of inguinal region and lower limb","Mycosis fungoides, lymph nodes of inguinal region and lower limb",Mycosis fungoides,9
C841,5,C8415,"Sezary disease, nodes of inguinal region and lower limb","Sezary disease, lymph nodes of inguinal region and lower limb",Sezary disease,9
C844,5,C8445,"Prph T-cell lymph, not class, nodes of ing rgn and low limb","Peripheral T-cell lymphoma, not classified, lymph nodes of inguinal region and lower limb","Peripheral T-cell lymphoma, not classified",9
C846,5,C8465,"Anaplstc lg cell lymph, ALK-pos, nodes of ing rgn & low lmb","Anaplastic large cell lymphoma, ALK-positive, lymph nodes of inguinal region and lower limb","Anaplastic large cell lymphoma, ALK-positive",9
C847,5,C8475,"Anaplstc lg cell lymph, ALK-neg, nodes of ing rgn & low lmb","Anaplastic large cell lymphoma, ALK-negative, lymph nodes of inguinal region and lower limb","Anaplastic large cell lymphoma, ALK-negative",9
C84A,5,C84A5,"Cutan T-cell lymph, unsp, nodes of ing region and lower limb","Cutaneous T-cell lymphoma, unspecified, lymph nodes of inguinal region and lower limb","Cutaneous T-cell lymphoma, unspecified",9
C84Z,5,C84Z5,"Oth mature T/NK-cell lymph, nodes of ing rgn and lower limb","Other mature T/NK-cell lymphomas, lymph nodes of inguinal region and lower limb",Other mature T/NK-cell lymphomas,9
C849,5,C8495,"Mature T/NK-cell lymph, unsp, nodes of ing rgn and low limb","Mature T/NK-cell lymphomas, unspecified, lymph nodes of inguinal region and lower limb","Mature T/NK-cell lymphomas, unspecified",9
C851,5,C8515,"Unsp B-cell lymphoma, nodes of ing region and lower limb","Unspecified B-cell lymphoma, lymph nodes of inguinal region and lower limb",Unspecified B-cell lymphoma,9
C852,5,C8525,"Mediastnl lg B-cell lymph, nodes of ing rgn and lower limb","Mediastinal (thymic) large B-cell lymphoma, lymph nodes of inguinal region and lower limb",Mediastinal (thymic) large B-cell lymphoma,9
C858,5,C8585,"Oth types of non-hodg lymph, nodes of ing rgn and lower limb","Other specified types of non-Hodgkin lymphoma, lymph nodes of inguinal region and lower limb",Other specified types of non-Hodgkin lymphoma,9
C859,5,C8595,"Non-hodg lymphoma, unsp, nodes of ing region and lower limb","Non-Hodgkin lymphoma, unspecified, lymph nodes of inguinal region and lower limb","Non-Hodgkin lymphoma, unspecified",9
C86,5,C865,Angioimmunoblastic T-cell lymphoma,Angioimmunoblastic T-cell lymphoma,Other specified types of T/NK-cell lymphoma,9
D000,5,D0005,Carcinoma in situ of hard palate,Carcinoma in situ of hard palate,"Carcinoma in situ of lip, oral cavity and pharynx",9
D12,5,D125,Benign neoplasm of sigmoid colon,Benign neoplasm of sigmoid colon,"Benign neoplasm of colon, rectum, anus and anal canal",9
D361,5,D3615,Benign neoplm of prph nerves and autonm nervous sys of abd,Benign neoplasm of peripheral nerves and autonomic nervous system of abdomen,Benign neoplasm of peripheral nerves and autonomic nervous system,9
D3A02,5,D3A025,Benign carcinoid tumor of the sigmoid colon,Benign carcinoid tumor of the sigmoid colon,"Benign carcinoid tumors of the appendix, large intestine, and rectum",9
D3A09,5,D3A095,"Benign carcinoid tumor of the midgut, unspecified","Benign carcinoid tumor of the midgut, unspecified",Benign carcinoid tumors of other sites,9
D38,5,D385,Neoplasm of uncertain behavior of other respiratory organs,Neoplasm of uncertain behavior of other respiratory organs,Neoplasm of uncertain behavior of middle ear and respiratory and intrathoracic organs,9
D48,5,D485,Neoplasm of uncertain behavior of skin,Neoplasm of uncertain behavior of skin,Neoplasm of uncertain behavior of other and unspecified sites,9
D56,5,D565,Hemoglobin E-beta thalassemia,Hemoglobin E-beta thalassemia,Thalassemia,9
D59,5,D595,Paroxysmal nocturnal hemoglobinuria [Marchiafava-Micheli],Paroxysmal nocturnal hemoglobinuria [Marchiafava-Micheli],Acquired hemolytic anemia,9
D7282,5,D72825,Bandemia,Bandemia,Elevated white blood cell count,9
D73,5,D735,Infarction of spleen,Infarction of spleen,Diseases of spleen,9
E7031,8,E70318,Other ocular albinism,Other ocular albinism,Ocular albinism,9
D80,5,D805,Immunodeficiency with increased immunoglobulin M [IgM],Immunodeficiency with increased immunoglobulin M [IgM],Immunodeficiency with predominantly antibody defects,9
D81,5,D815,Purine nucleoside phosphorylase [PNP] deficiency,Purine nucleoside phosphorylase [PNP] deficiency,Combined immunodeficiencies,9
D868,5,D8685,Sarcoid myocarditis,Sarcoid myocarditis,Sarcoidosis of other sites,9
E03,5,E035,Myxedema coma,Myxedema coma,Other hypothyroidism,9
E06,5,E065,Other chronic thyroiditis,Other chronic thyroiditis,Thyroiditis,9
E21,5,E215,"Disorder of parathyroid gland, unspecified","Disorder of parathyroid gland, unspecified",Hyperparathyroidism and other disorders of parathyroid gland,9
E50,5,E505,Vitamin A deficiency with night blindness,Vitamin A deficiency with night blindness,Vitamin A deficiency,9
E61,5,E615,Molybdenum deficiency,Molybdenum deficiency,Deficiency of other nutrient elements,9
E87,5,E875,Hyperkalemia,Hyperkalemia,"Other disorders of fluid, electrolyte and acid-base balance",9
F20,5,F205,Residual schizophrenia,Residual schizophrenia,Schizophrenia,9
F317,5,F3175,"Bipolar disord, in partial remis, most recent epsd depress","Bipolar disorder, in partial remission, most recent episode depressed","Bipolar disorder, currently in remission",9
F32,5,F325,"Major depressive disorder, single episode, in full remission","Major depressive disorder, single episode, in full remission","Major depressive disorder, single episode",9
F432,5,F4325,Adjustment disorder w mixed disturb of emotions and conduct,Adjustment disorder with mixed disturbance of emotions and conduct,Adjustment disorders,9
F44,5,F445,Conversion disorder with seizures or convulsions,Conversion disorder with seizures or convulsions,Dissociative and conversion disorders,9
F510,5,F5105,Insomnia due to other mental disorder,Insomnia due to other mental disorder,Insomnia not due to a substance or known physiological condition,9
F60,5,F605,Obsessive-compulsive personality disorder,Obsessive-compulsive personality disorder,Specific personality disorders,9
F84,5,F845,Asperger's syndrome,Asperger's syndrome,Pervasive developmental disorders,9
G122,5,G1225,Progressive spinal muscle atrophy,Progressive spinal muscle atrophy,Motor neuron disease,9
G25,5,G255,Other chorea,Other chorea,Other extrapyramidal and movement disorders,9
G318,5,G3185,Corticobasal degeneration,Corticobasal degeneration,Other specified degenerative diseases of nervous system,9
G37,5,G375,Concentric sclerosis [Balo] of central nervous system,Concentric sclerosis [Balo] of central nervous system,Other demyelinating diseases of central nervous system,9
G448,5,G4485,Primary stabbing headache,Primary stabbing headache,Other specified headache syndromes,9
G46,5,G465,Pure motor lacunar syndrome,Pure motor lacunar syndrome,Vascular syndromes of brain in cerebrovascular diseases,9
G472,5,G4725,"Circadian rhythm sleep disorder, jet lag type","Circadian rhythm sleep disorder, jet lag type",Circadian rhythm sleep disorders,9
G473,5,G4735,Congenital central alveolar hypoventilation syndrome,Congenital central alveolar hypoventilation syndrome,Sleep apnea,9
G54,5,G545,Neuralgic amyotrophy,Neuralgic amyotrophy,Nerve root and plexus disorders,9
A04,6,A046,Enteritis due to Yersinia enterocolitica,Enteritis due to Yersinia enterocolitica,Other bacterial intestinal infections,9
A06,6,A066,Amebic brain abscess,Amebic brain abscess,Amebiasis,9
A15,6,A156,Tuberculous pleurisy,Tuberculous pleurisy,Respiratory tuberculosis,9
A181,6,A1816,Tuberculosis of cervix,Tuberculosis of cervix,Tuberculosis of genitourinary system,9
A368,6,A3686,Diphtheritic conjunctivitis,Diphtheritic conjunctivitis,Other diphtheria,9
A500,6,A5006,Early cutaneous congenital syphilis,Early cutaneous congenital syphilis,"Early congenital syphilis, symptomatic",9
A505,6,A5056,Late congenital syphilitic osteochondropathy,Late congenital syphilitic osteochondropathy,"Other late congenital syphilis, symptomatic",9
A514,6,A5146,Secondary syphilitic osteopathy,Secondary syphilitic osteopathy,Other secondary syphilis,9
A520,6,A5206,Other syphilitic heart involvement,Other syphilitic heart involvement,Cardiovascular and cerebrovascular syphilis,9
A521,6,A5216,Charcot's arthropathy (tabetic),Charcot's arthropathy (tabetic),Symptomatic neurosyphilis,9
A527,6,A5276,Other genitourinary symptomatic late syphilis,Other genitourinary symptomatic late syphilis,Other symptomatic late syphilis,9
A548,6,A5486,Gonococcal sepsis,Gonococcal sepsis,Other gonococcal infections,9
A66,6,A666,Bone and joint lesions of yaws,Bone and joint lesions of yaws,Yaws,9
A83,6,A836,Rocio virus disease,Rocio virus disease,Mosquito-borne viral encephalitis,9
B35,6,B356,Tinea cruris,Tinea cruris,Dermatophytosis,9
C00,6,C006,"Malignant neoplasm of commissure of lip, unspecified","Malignant neoplasm of commissure of lip, unspecified",Malignant neoplasm of lip,9
C16,6,C166,"Malignant neoplasm of greater curvature of stomach, unsp","Malignant neoplasm of greater curvature of stomach, unspecified",Malignant neoplasm of stomach,9
C18,6,C186,Malignant neoplasm of descending colon,Malignant neoplasm of descending colon,Malignant neoplasm of colon,9
C67,6,C676,Malignant neoplasm of ureteric orifice,Malignant neoplasm of ureteric orifice,Malignant neoplasm of bladder,9
C71,6,C716,Malignant neoplasm of cerebellum,Malignant neoplasm of cerebellum,Malignant neoplasm of brain,9
C7A02,6,C7A026,Malignant carcinoid tumor of the rectum,Malignant carcinoid tumor of the rectum,"Malignant carcinoid tumors of the appendix, large intestine, and rectum",9
C7A09,6,C7A096,"Malignant carcinoid tumor of the hindgut, unspecified","Malignant carcinoid tumor of the hindgut, unspecified",Malignant carcinoid tumors of other sites,9
C810,6,C8106,"Nodular lymphocyte predom Hodgkin lymphoma, intrapelv nodes","Nodular lymphocyte predominant Hodgkin lymphoma, intrapelvic lymph nodes",Nodular lymphocyte predominant Hodgkin lymphoma,9
C811,6,C8116,"Nodular sclerosis Hodgkin lymphoma, intrapelvic lymph nodes","Nodular sclerosis Hodgkin lymphoma, intrapelvic lymph nodes",Nodular sclerosis Hodgkin lymphoma,9
C812,6,C8126,"Mixed cellularity Hodgkin lymphoma, intrapelvic lymph nodes","Mixed cellularity Hodgkin lymphoma, intrapelvic lymph nodes",Mixed cellularity Hodgkin lymphoma,9
C813,6,C8136,"Lymphocyte depleted Hodgkin lymphoma, intrapelv lymph nodes","Lymphocyte depleted Hodgkin lymphoma, intrapelvic lymph nodes",Lymphocyte depleted Hodgkin lymphoma,9
C814,6,C8146,"Lymphocyte-rich Hodgkin lymphoma, intrapelvic lymph nodes","Lymphocyte-rich Hodgkin lymphoma, intrapelvic lymph nodes",Lymphocyte-rich Hodgkin lymphoma,9
C817,6,C8176,"Other Hodgkin lymphoma, intrapelvic lymph nodes","Other Hodgkin lymphoma, intrapelvic lymph nodes",Other Hodgkin lymphoma,9
C819,6,C8196,"Hodgkin lymphoma, unspecified, intrapelvic lymph nodes","Hodgkin lymphoma, unspecified, intrapelvic lymph nodes","Hodgkin lymphoma, unspecified",9
C820,6,C8206,"Follicular lymphoma grade I, intrapelvic lymph nodes","Follicular lymphoma grade I, intrapelvic lymph nodes",Follicular lymphoma grade I,9
C821,6,C8216,"Follicular lymphoma grade II, intrapelvic lymph nodes","Follicular lymphoma grade II, intrapelvic lymph nodes",Follicular lymphoma grade II,9
C822,6,C8226,"Follicular lymphoma grade III, unsp, intrapelvic lymph nodes","Follicular lymphoma grade III, unspecified, intrapelvic lymph nodes","Follicular lymphoma grade III, unspecified",9
C823,6,C8236,"Follicular lymphoma grade IIIa, intrapelvic lymph nodes","Follicular lymphoma grade IIIa, intrapelvic lymph nodes",Follicular lymphoma grade IIIa,9
C824,6,C8246,"Follicular lymphoma grade IIIb, intrapelvic lymph nodes","Follicular lymphoma grade IIIb, intrapelvic lymph nodes",Follicular lymphoma grade IIIb,9
C825,6,C8256,"Diffuse follicle center lymphoma, intrapelvic lymph nodes","Diffuse follicle center lymphoma, intrapelvic lymph nodes",Diffuse follicle center lymphoma,9
C826,6,C8266,"Cutaneous follicle center lymphoma, intrapelvic lymph nodes","Cutaneous follicle center lymphoma, intrapelvic lymph nodes",Cutaneous follicle center lymphoma,9
C828,6,C8286,"Other types of follicular lymphoma, intrapelvic lymph nodes","Other types of follicular lymphoma, intrapelvic lymph nodes",Other types of follicular lymphoma,9
C829,6,C8296,"Follicular lymphoma, unspecified, intrapelvic lymph nodes","Follicular lymphoma, unspecified, intrapelvic lymph nodes","Follicular lymphoma, unspecified",9
C830,6,C8306,"Small cell B-cell lymphoma, intrapelvic lymph nodes","Small cell B-cell lymphoma, intrapelvic lymph nodes",Small cell B-cell lymphoma,9
C831,6,C8316,"Mantle cell lymphoma, intrapelvic lymph nodes","Mantle cell lymphoma, intrapelvic lymph nodes",Mantle cell lymphoma,9
C833,6,C8336,"Diffuse large B-cell lymphoma, intrapelvic lymph nodes","Diffuse large B-cell lymphoma, intrapelvic lymph nodes",Diffuse large B-cell lymphoma,9
C835,6,C8356,"Lymphoblastic (diffuse) lymphoma, intrapelvic lymph nodes","Lymphoblastic (diffuse) lymphoma, intrapelvic lymph nodes",Lymphoblastic (diffuse) lymphoma,9
C837,6,C8376,"Burkitt lymphoma, intrapelvic lymph nodes","Burkitt lymphoma, intrapelvic lymph nodes",Burkitt lymphoma,9
C838,6,C8386,"Other non-follicular lymphoma, intrapelvic lymph nodes","Other non-follicular lymphoma, intrapelvic lymph nodes",Other non-follicular lymphoma,9
C839,6,C8396,"Non-follic (diffuse) lymphoma, unsp, intrapelvic lymph nodes","Non-follicular (diffuse) lymphoma, unspecified, intrapelvic lymph nodes","Non-follicular (diffuse) lymphoma, unspecified",9
C840,6,C8406,"Mycosis fungoides, intrapelvic lymph nodes","Mycosis fungoides, intrapelvic lymph nodes",Mycosis fungoides,9
C841,6,C8416,"Sezary disease, intrapelvic lymph nodes","Sezary disease, intrapelvic lymph nodes",Sezary disease,9
C844,6,C8446,"Peripheral T-cell lymphoma, not classified, intrapelv nodes","Peripheral T-cell lymphoma, not classified, intrapelvic lymph nodes","Peripheral T-cell lymphoma, not classified",9
C846,6,C8466,"Anaplastic large cell lymphoma, ALK-pos, intrapelv nodes","Anaplastic large cell lymphoma, ALK-positive, intrapelvic lymph nodes","Anaplastic large cell lymphoma, ALK-positive",9
C847,6,C8476,"Anaplastic large cell lymphoma, ALK-neg, intrapelv nodes","Anaplastic large cell lymphoma, ALK-negative, intrapelvic lymph nodes","Anaplastic large cell lymphoma, ALK-negative",9
C84A,6,C84A6,"Cutaneous T-cell lymphoma, unsp, intrapelvic lymph nodes","Cutaneous T-cell lymphoma, unspecified, intrapelvic lymph nodes","Cutaneous T-cell lymphoma, unspecified",9
C84Z,6,C84Z6,"Other mature T/NK-cell lymphomas, intrapelvic lymph nodes","Other mature T/NK-cell lymphomas, intrapelvic lymph nodes",Other mature T/NK-cell lymphomas,9
C849,6,C8496,"Mature T/NK-cell lymphomas, unsp, intrapelvic lymph nodes","Mature T/NK-cell lymphomas, unspecified, intrapelvic lymph nodes","Mature T/NK-cell lymphomas, unspecified",9
C851,6,C8516,"Unspecified B-cell lymphoma, intrapelvic lymph nodes","Unspecified B-cell lymphoma, intrapelvic lymph nodes",Unspecified B-cell lymphoma,9
C852,6,C8526,"Mediastinal (thymic) large B-cell lymphoma, intrapelv nodes","Mediastinal (thymic) large B-cell lymphoma, intrapelvic lymph nodes",Mediastinal (thymic) large B-cell lymphoma,9
C858,6,C8586,"Oth types of non-Hodgkin lymphoma, intrapelvic lymph nodes","Other specified types of non-Hodgkin lymphoma, intrapelvic lymph nodes",Other specified types of non-Hodgkin lymphoma,9
C859,6,C8596,"Non-Hodgkin lymphoma, unspecified, intrapelvic lymph nodes","Non-Hodgkin lymphoma, unspecified, intrapelvic lymph nodes","Non-Hodgkin lymphoma, unspecified",9
C86,6,C866,Primary cutaneous CD30-positive T-cell proliferations,Primary cutaneous CD30-positive T-cell proliferations,Other specified types of T/NK-cell lymphoma,9
D000,6,D0006,Carcinoma in situ of floor of mouth,Carcinoma in situ of floor of mouth,"Carcinoma in situ of lip, oral cavity and pharynx",9
D12,6,D126,"Benign neoplasm of colon, unspecified","Benign neoplasm of colon, unspecified","Benign neoplasm of colon, rectum, anus and anal canal",9
D361,6,D3616,Benign neoplm of prph nerves and autonm nrv sys of pelvis,Benign neoplasm of peripheral nerves and autonomic nervous system of pelvis,Benign neoplasm of peripheral nerves and autonomic nervous system,9
D3A02,6,D3A026,Benign carcinoid tumor of the rectum,Benign carcinoid tumor of the rectum,"Benign carcinoid tumors of the appendix, large intestine, and rectum",9
D3A09,6,D3A096,"Benign carcinoid tumor of the hindgut, unspecified","Benign carcinoid tumor of the hindgut, unspecified",Benign carcinoid tumors of other sites,9
D38,6,D386,"Neoplasm of uncertain behavior of respiratory organ, unsp","Neoplasm of uncertain behavior of respiratory organ, unspecified",Neoplasm of uncertain behavior of middle ear and respiratory and intrathoracic organs,9
D59,6,D596,Hemoglobinuria due to hemolysis from other external causes,Hemoglobinuria due to hemolysis from other external causes,Acquired hemolytic anemia,9
A75,9,A759,"Typhus fever, unspecified","Typhus fever, unspecified",Typhus fever,9
D80,6,D806,Antibody defic w near-norm immunoglob or w hyperimmunoglob,Antibody deficiency with near-normal immunoglobulins or with hyperimmunoglobulinemia,Immunodeficiency with predominantly antibody defects,9
D81,6,D816,Major histocompatibility complex class I deficiency,Major histocompatibility complex class I deficiency,Combined immunodeficiencies,9
D868,6,D8686,Sarcoid arthropathy,Sarcoid arthropathy,Sarcoidosis of other sites,9
E23,6,E236,Other disorders of pituitary gland,Other disorders of pituitary gland,Hypofunction and other disorders of the pituitary gland,9
E50,6,E506,Vitamin A deficiency with xerophthalmic scars of cornea,Vitamin A deficiency with xerophthalmic scars of cornea,Vitamin A deficiency,9
E61,6,E616,Vanadium deficiency,Vanadium deficiency,Deficiency of other nutrient elements,9
E87,6,E876,Hypokalemia,Hypokalemia,"Other disorders of fluid, electrolyte and acid-base balance",9
F317,6,F3176,"Bipolar disorder, in full remis, most recent episode depress","Bipolar disorder, in full remission, most recent episode depressed","Bipolar disorder, currently in remission",9
F44,6,F446,Conversion disorder with sensory symptom or deficit,Conversion disorder with sensory symptom or deficit,Dissociative and conversion disorders,9
F60,6,F606,Avoidant personality disorder,Avoidant personality disorder,Specific personality disorders,9
G46,6,G466,Pure sensory lacunar syndrome,Pure sensory lacunar syndrome,Vascular syndromes of brain in cerebrovascular diseases,9
G472,6,G4726,"Circadian rhythm sleep disorder, shift work type","Circadian rhythm sleep disorder, shift work type",Circadian rhythm sleep disorders,9
G473,6,G4736,Sleep related hypoventilation in conditions classd elswhr,Sleep related hypoventilation in conditions classified elsewhere,Sleep apnea,9
G54,6,G546,Phantom limb syndrome with pain,Phantom limb syndrome with pain,Nerve root and plexus disorders,9
A06,7,A067,Cutaneous amebiasis,Cutaneous amebiasis,Amebiasis,9
A15,7,A157,Primary respiratory tuberculosis,Primary respiratory tuberculosis,Respiratory tuberculosis,9
A181,7,A1817,Tuberculous female pelvic inflammatory disease,Tuberculous female pelvic inflammatory disease,Tuberculosis of genitourinary system,9
A20,7,A207,Septicemic plague,Septicemic plague,Plague,9
A21,7,A217,Generalized tularemia,Generalized tularemia,Tularemia,9
A22,7,A227,Anthrax sepsis,Anthrax sepsis,Anthrax,9
A26,7,A267,Erysipelothrix sepsis,Erysipelothrix sepsis,Erysipeloid,9
A42,7,A427,Actinomycotic sepsis,Actinomycotic sepsis,Actinomycosis,9
A500,7,A5007,Early mucocutaneous congenital syphilis,Early mucocutaneous congenital syphilis,"Early congenital syphilis, symptomatic",9
A505,7,A5057,Syphilitic saddle nose,Syphilitic saddle nose,"Other late congenital syphilis, symptomatic",9
A521,7,A5217,General paresis,General paresis,Symptomatic neurosyphilis,9
A527,7,A5277,Syphilis of bone and joint,Syphilis of bone and joint,Other symptomatic late syphilis,9
A66,7,A667,Other manifestations of yaws,Other manifestations of yaws,Yaws,9
B38,7,B387,Disseminated coccidioidomycosis,Disseminated coccidioidomycosis,Coccidioidomycosis,9
B40,7,B407,Disseminated blastomycosis,Disseminated blastomycosis,Blastomycosis,9
B41,7,B417,Disseminated paracoccidioidomycosis,Disseminated paracoccidioidomycosis,Paracoccidioidomycosis,9
B42,7,B427,Disseminated sporotrichosis,Disseminated sporotrichosis,Sporotrichosis,9
B44,7,B447,Disseminated aspergillosis,Disseminated aspergillosis,Aspergillosis,9
B45,7,B457,Disseminated cryptococcosis,Disseminated cryptococcosis,Cryptococcosis,9
B78,7,B787,Disseminated strongyloidiasis,Disseminated strongyloidiasis,Strongyloidiasis,9
C18,7,C187,Malignant neoplasm of sigmoid colon,Malignant neoplasm of sigmoid colon,Malignant neoplasm of colon,9
C22,7,C227,Other specified carcinomas of liver,Other specified carcinomas of liver,Malignant neoplasm of liver and intrahepatic bile ducts,9
C25,7,C257,Malignant neoplasm of other parts of pancreas,Malignant neoplasm of other parts of pancreas,Malignant neoplasm of pancreas,9
C45,7,C457,Mesothelioma of other sites,Mesothelioma of other sites,Mesothelioma,9
C67,7,C677,Malignant neoplasm of urachus,Malignant neoplasm of urachus,Malignant neoplasm of bladder,9
C71,7,C717,Malignant neoplasm of brain stem,Malignant neoplasm of brain stem,Malignant neoplasm of brain,9
C810,7,C8107,"Nodular lymphocyte predominant Hodgkin lymphoma, spleen","Nodular lymphocyte predominant Hodgkin lymphoma, spleen",Nodular lymphocyte predominant Hodgkin lymphoma,9
C811,7,C8117,"Nodular sclerosis Hodgkin lymphoma, spleen","Nodular sclerosis Hodgkin lymphoma, spleen",Nodular sclerosis Hodgkin lymphoma,9
C812,7,C8127,"Mixed cellularity Hodgkin lymphoma, spleen","Mixed cellularity Hodgkin lymphoma, spleen",Mixed cellularity Hodgkin lymphoma,9
C813,7,C8137,"Lymphocyte depleted Hodgkin lymphoma, spleen","Lymphocyte depleted Hodgkin lymphoma, spleen",Lymphocyte depleted Hodgkin lymphoma,9
C814,7,C8147,"Lymphocyte-rich Hodgkin lymphoma, spleen","Lymphocyte-rich Hodgkin lymphoma, spleen",Lymphocyte-rich Hodgkin lymphoma,9
C817,7,C8177,"Other Hodgkin lymphoma, spleen","Other Hodgkin lymphoma, spleen",Other Hodgkin lymphoma,9
C819,7,C8197,"Hodgkin lymphoma, unspecified, spleen","Hodgkin lymphoma, unspecified, spleen","Hodgkin lymphoma, unspecified",9
C820,7,C8207,"Follicular lymphoma grade I, spleen","Follicular lymphoma grade I, spleen",Follicular lymphoma grade I,9
C821,7,C8217,"Follicular lymphoma grade II, spleen","Follicular lymphoma grade II, spleen",Follicular lymphoma grade II,9
C822,7,C8227,"Follicular lymphoma grade III, unspecified, spleen","Follicular lymphoma grade III, unspecified, spleen","Follicular lymphoma grade III, unspecified",9
C823,7,C8237,"Follicular lymphoma grade IIIa, spleen","Follicular lymphoma grade IIIa, spleen",Follicular lymphoma grade IIIa,9
C824,7,C8247,"Follicular lymphoma grade IIIb, spleen","Follicular lymphoma grade IIIb, spleen",Follicular lymphoma grade IIIb,9
C825,7,C8257,"Diffuse follicle center lymphoma, spleen","Diffuse follicle center lymphoma, spleen",Diffuse follicle center lymphoma,9
C826,7,C8267,"Cutaneous follicle center lymphoma, spleen","Cutaneous follicle center lymphoma, spleen",Cutaneous follicle center lymphoma,9
C828,7,C8287,"Other types of follicular lymphoma, spleen","Other types of follicular lymphoma, spleen",Other types of follicular lymphoma,9
C829,7,C8297,"Follicular lymphoma, unspecified, spleen","Follicular lymphoma, unspecified, spleen","Follicular lymphoma, unspecified",9
C830,7,C8307,"Small cell B-cell lymphoma, spleen","Small cell B-cell lymphoma, spleen",Small cell B-cell lymphoma,9
C831,7,C8317,"Mantle cell lymphoma, spleen","Mantle cell lymphoma, spleen",Mantle cell lymphoma,9
C833,7,C8337,"Diffuse large B-cell lymphoma, spleen","Diffuse large B-cell lymphoma, spleen",Diffuse large B-cell lymphoma,9
C835,7,C8357,"Lymphoblastic (diffuse) lymphoma, spleen","Lymphoblastic (diffuse) lymphoma, spleen",Lymphoblastic (diffuse) lymphoma,9
C837,7,C8377,"Burkitt lymphoma, spleen","Burkitt lymphoma, spleen",Burkitt lymphoma,9
C838,7,C8387,"Other non-follicular lymphoma, spleen","Other non-follicular lymphoma, spleen",Other non-follicular lymphoma,9
C839,7,C8397,"Non-follicular (diffuse) lymphoma, unspecified, spleen","Non-follicular (diffuse) lymphoma, unspecified, spleen","Non-follicular (diffuse) lymphoma, unspecified",9
C840,7,C8407,"Mycosis fungoides, spleen","Mycosis fungoides, spleen",Mycosis fungoides,9
C841,7,C8417,"Sezary disease, spleen","Sezary disease, spleen",Sezary disease,9
C844,7,C8447,"Peripheral T-cell lymphoma, not classified, spleen","Peripheral T-cell lymphoma, not classified, spleen","Peripheral T-cell lymphoma, not classified",9
C846,7,C8467,"Anaplastic large cell lymphoma, ALK-positive, spleen","Anaplastic large cell lymphoma, ALK-positive, spleen","Anaplastic large cell lymphoma, ALK-positive",9
C847,7,C8477,"Anaplastic large cell lymphoma, ALK-negative, spleen","Anaplastic large cell lymphoma, ALK-negative, spleen","Anaplastic large cell lymphoma, ALK-negative",9
C84A,7,C84A7,"Cutaneous T-cell lymphoma, unspecified, spleen","Cutaneous T-cell lymphoma, unspecified, spleen","Cutaneous T-cell lymphoma, unspecified",9
C84Z,7,C84Z7,"Other mature T/NK-cell lymphomas, spleen","Other mature T/NK-cell lymphomas, spleen",Other mature T/NK-cell lymphomas,9
C849,7,C8497,"Mature T/NK-cell lymphomas, unspecified, spleen","Mature T/NK-cell lymphomas, unspecified, spleen","Mature T/NK-cell lymphomas, unspecified",9
C851,7,C8517,"Unspecified B-cell lymphoma, spleen","Unspecified B-cell lymphoma, spleen",Unspecified B-cell lymphoma,9
C852,7,C8527,"Mediastinal (thymic) large B-cell lymphoma, spleen","Mediastinal (thymic) large B-cell lymphoma, spleen",Mediastinal (thymic) large B-cell lymphoma,9
C858,7,C8587,"Other specified types of non-Hodgkin lymphoma, spleen","Other specified types of non-Hodgkin lymphoma, spleen",Other specified types of non-Hodgkin lymphoma,9
C859,7,C8597,"Non-Hodgkin lymphoma, unspecified, spleen","Non-Hodgkin lymphoma, unspecified, spleen","Non-Hodgkin lymphoma, unspecified",9
D000,7,D0007,Carcinoma in situ of tongue,Carcinoma in situ of tongue,"Carcinoma in situ of lip, oral cavity and pharynx",9
D06,7,D067,Carcinoma in situ of other parts of cervix,Carcinoma in situ of other parts of cervix,Carcinoma in situ of cervix uteri,9
D11,7,D117,Benign neoplasm of other major salivary glands,Benign neoplasm of other major salivary glands,Benign neoplasm of major salivary glands,9
D12,7,D127,Benign neoplasm of rectosigmoid junction,Benign neoplasm of rectosigmoid junction,"Benign neoplasm of colon, rectum, anus and anal canal",9
D15,7,D157,Benign neoplasm of other specified intrathoracic organs,Benign neoplasm of other specified intrathoracic organs,Benign neoplasm of other and unspecified intrathoracic organs,9
D19,7,D197,Benign neoplasm of mesothelial tissue of other sites,Benign neoplasm of mesothelial tissue of other sites,Benign neoplasm of mesothelial tissue,9
D26,7,D267,Other benign neoplasm of other parts of uterus,Other benign neoplasm of other parts of uterus,Other benign neoplasms of uterus,9
D28,7,D287,Benign neoplasm of other specified female genital organs,Benign neoplasm of other specified female genital organs,Benign neoplasm of other and unspecified female genital organs,9
D33,7,D337,Benign neoplasm of oth parts of central nervous system,Benign neoplasm of other specified parts of central nervous system,Benign neoplasm of brain and other parts of central nervous system,9
D361,7,D3617,"Ben neoplm of prph nerves and autonm nrv sys of trunk, unsp","Benign neoplasm of peripheral nerves and autonomic nervous system of trunk, unspecified",Benign neoplasm of peripheral nerves and autonomic nervous system,9
D80,7,D807,Transient hypogammaglobulinemia of infancy,Transient hypogammaglobulinemia of infancy,Immunodeficiency with predominantly antibody defects,9
D81,7,D817,Major histocompatibility complex class II deficiency,Major histocompatibility complex class II deficiency,Combined immunodeficiencies,9
D868,7,D8687,Sarcoid myositis,Sarcoid myositis,Sarcoidosis of other sites,9
E23,7,E237,"Disorder of pituitary gland, unspecified","Disorder of pituitary gland, unspecified",Hypofunction and other disorders of the pituitary gland,9
E50,7,E507,Other ocular manifestations of vitamin A deficiency,Other ocular manifestations of vitamin A deficiency,Vitamin A deficiency,9
E61,7,E617,Deficiency of multiple nutrient elements,Deficiency of multiple nutrient elements,Deficiency of other nutrient elements,9
F317,7,F3177,"Bipolar disord, in partial remis, most recent episode mixed","Bipolar disorder, in partial remission, most recent episode mixed","Bipolar disorder, currently in remission",9
F44,7,F447,Conversion disorder with mixed symptom presentation,Conversion disorder with mixed symptom presentation,Dissociative and conversion disorders,9
F60,7,F607,Dependent personality disorder,Dependent personality disorder,Specific personality disorders,9
G46,7,G467,Other lacunar syndromes,Other lacunar syndromes,Vascular syndromes of brain in cerebrovascular diseases,9
G472,7,G4727,Circadian rhythm sleep disorder in conditions classd elswhr,Circadian rhythm sleep disorder in conditions classified elsewhere,Circadian rhythm sleep disorders,9
G473,7,G4737,Central sleep apnea in conditions classified elsewhere,Central sleep apnea in conditions classified elsewhere,Sleep apnea,9
G52,7,G527,Disorders of multiple cranial nerves,Disorders of multiple cranial nerves,Disorders of other cranial nerves,9
G54,7,G547,Phantom limb syndrome without pain,Phantom limb syndrome without pain,Nerve root and plexus disorders,9
A03,8,A038,Other shigellosis,Other shigellosis,Shigellosis,9
A05,8,A058,Other specified bacterial foodborne intoxications,Other specified bacterial foodborne intoxications,"Other bacterial foodborne intoxications, not elsewhere classified",9
A07,8,A078,Other specified protozoal intestinal diseases,Other specified protozoal intestinal diseases,Other protozoal intestinal diseases,9
A15,8,A158,Other respiratory tuberculosis,Other respiratory tuberculosis,Respiratory tuberculosis,9
A181,8,A1818,Tuberculosis of other female genital organs,Tuberculosis of other female genital organs,Tuberculosis of genitourinary system,9
A19,8,A198,Other miliary tuberculosis,Other miliary tuberculosis,Miliary tuberculosis,9
A20,8,A208,Other forms of plague,Other forms of plague,Plague,9
A21,8,A218,Other forms of tularemia,Other forms of tularemia,Tularemia,9
A22,8,A228,Other forms of anthrax,Other forms of anthrax,Anthrax,9
A23,8,A238,Other brucellosis,Other brucellosis,Brucellosis,9
A26,8,A268,Other forms of erysipeloid,Other forms of erysipeloid,Erysipeloid,9
A28,8,A288,"Oth zoonotic bacterial diseases, not elsewhere classified","Other specified zoonotic bacterial diseases, not elsewhere classified","Other zoonotic bacterial diseases, not elsewhere classified",9
A30,8,A308,Other forms of leprosy,Other forms of leprosy,Leprosy [Hansen's disease],9
A31,8,A318,Other mycobacterial infections,Other mycobacterial infections,Infection due to other mycobacteria,9
A38,8,A388,Scarlet fever with other complications,Scarlet fever with other complications,Scarlet fever,9
A40,8,A408,Other streptococcal sepsis,Other streptococcal sepsis,Streptococcal sepsis,9
A43,8,A438,Other forms of nocardiosis,Other forms of nocardiosis,Nocardiosis,9
A44,8,A448,Other forms of bartonellosis,Other forms of bartonellosis,Bartonellosis,9
A500,8,A5008,Early visceral congenital syphilis,Early visceral congenital syphilis,"Early congenital syphilis, symptomatic",9
A527,8,A5278,Syphilis of other musculoskeletal tissue,Syphilis of other musculoskeletal tissue,Other symptomatic late syphilis,9
A63,8,A638,Other specified predominantly sexually transmitted diseases,Other specified predominantly sexually transmitted diseases,"Other predominantly sexually transmitted diseases, not elsewhere classified",9
A66,8,A668,Latent yaws,Latent yaws,Yaws,9
A83,8,A838,Other mosquito-borne viral encephalitis,Other mosquito-borne viral encephalitis,Mosquito-borne viral encephalitis,9
A84,8,A848,Other tick-borne viral encephalitis,Other tick-borne viral encephalitis,Tick-borne viral encephalitis,9
A85,8,A858,Other specified viral encephalitis,Other specified viral encephalitis,"Other viral encephalitis, not elsewhere classified",9
A87,8,A878,Other viral meningitis,Other viral meningitis,Viral meningitis,9
A88,8,A888,Other specified viral infections of central nervous system,Other specified viral infections of central nervous system,"Other viral infections of central nervous system, not elsewhere classified",9
A93,8,A938,Other specified arthropod-borne viral fevers,Other specified arthropod-borne viral fevers,"Other arthropod-borne viral fevers, not elsewhere classified",9
A96,8,A968,Other arenaviral hemorrhagic fevers,Other arenaviral hemorrhagic fevers,Arenaviral hemorrhagic fever,9
A98,8,A988,Other specified viral hemorrhagic fevers,Other specified viral hemorrhagic fevers,"Other viral hemorrhagic fevers, not elsewhere classified",9
B07,8,B078,Other viral warts,Other viral warts,Viral warts,9
B18,8,B188,Other chronic viral hepatitis,Other chronic viral hepatitis,Chronic viral hepatitis,9
B25,8,B258,Other cytomegaloviral diseases,Other cytomegaloviral diseases,Cytomegaloviral disease,9
B30,8,B308,Other viral conjunctivitis,Other viral conjunctivitis,Viral conjunctivitis,9
B34,8,B348,Other viral infections of unspecified site,Other viral infections of unspecified site,Viral infection of unspecified site,9
B35,8,B358,Other dermatophytoses,Other dermatophytoses,Dermatophytosis,9
B36,8,B368,Other specified superficial mycoses,Other specified superficial mycoses,Other superficial mycoses,9
B41,8,B418,Other forms of paracoccidioidomycosis,Other forms of paracoccidioidomycosis,Paracoccidioidomycosis,9
B43,8,B438,Other forms of chromomycosis,Other forms of chromomycosis,Chromomycosis and pheomycotic abscess,9
B45,8,B458,Other forms of cryptococcosis,Other forms of cryptococcosis,Cryptococcosis,9
B46,8,B468,Other zygomycoses,Other zygomycoses,Zygomycosis,9
B48,8,B488,Other specified mycoses,Other specified mycoses,"Other mycoses, not elsewhere classified",9
B50,8,B508,Other severe and complicated Plasmodium falciparum malaria,Other severe and complicated Plasmodium falciparum malaria,Plasmodium falciparum malaria,9
B51,8,B518,Plasmodium vivax malaria with other complications,Plasmodium vivax malaria with other complications,Plasmodium vivax malaria,9
B52,8,B528,Plasmodium malariae malaria with other complications,Plasmodium malariae malaria with other complications,Plasmodium malariae malaria,9
B53,8,B538,"Other malaria, not elsewhere classified","Other malaria, not elsewhere classified",Other specified malaria,9
B65,8,B658,Other schistosomiasis,Other schistosomiasis,Schistosomiasis [bilharziasis],9
B66,8,B668,Other specified fluke infections,Other specified fluke infections,Other fluke infections,9
B71,8,B718,Other specified cestode infections,Other specified cestode infections,Other cestode infections,9
B74,8,B748,Other filariases,Other filariases,Filariasis,9
B76,8,B768,Other hookworm diseases,Other hookworm diseases,Hookworm diseases,9
B81,8,B818,Other specified intestinal helminthiases,Other specified intestinal helminthiases,"Other intestinal helminthiases, not elsewhere classified",9
B83,8,B838,Other specified helminthiases,Other specified helminthiases,Other helminthiases,9
B88,8,B888,Other specified infestations,Other specified infestations,Other infestations,9
B90,8,B908,Sequelae of tuberculosis of other organs,Sequelae of tuberculosis of other organs,Sequelae of tuberculosis,9
C820,8,C8208,"Follicular lymphoma grade I, lymph nodes of multiple sites","Follicular lymphoma grade I, lymph nodes of multiple sites",Follicular lymphoma grade I,9
B94,8,B948,Sequelae of oth infectious and parasitic diseases,Sequelae of other specified infectious and parasitic diseases,Sequelae of other and unspecified infectious and parasitic diseases,9
B99,8,B998,Other infectious disease,Other infectious disease,Other and unspecified infectious diseases,9
C00,8,C008,Malignant neoplasm of overlapping sites of lip,Malignant neoplasm of overlapping sites of lip,Malignant neoplasm of lip,9
C02,8,C028,Malignant neoplasm of overlapping sites of tongue,Malignant neoplasm of overlapping sites of tongue,Malignant neoplasm of other and unspecified parts of tongue,9
C04,8,C048,Malignant neoplasm of overlapping sites of floor of mouth,Malignant neoplasm of overlapping sites of floor of mouth,Malignant neoplasm of floor of mouth,9
C05,8,C058,Malignant neoplasm of overlapping sites of palate,Malignant neoplasm of overlapping sites of palate,Malignant neoplasm of palate,9
C09,8,C098,Malignant neoplasm of overlapping sites of tonsil,Malignant neoplasm of overlapping sites of tonsil,Malignant neoplasm of tonsil,9
C10,8,C108,Malignant neoplasm of overlapping sites of oropharynx,Malignant neoplasm of overlapping sites of oropharynx,Malignant neoplasm of oropharynx,9
C11,8,C118,Malignant neoplasm of overlapping sites of nasopharynx,Malignant neoplasm of overlapping sites of nasopharynx,Malignant neoplasm of nasopharynx,9
C13,8,C138,Malignant neoplasm of overlapping sites of hypopharynx,Malignant neoplasm of overlapping sites of hypopharynx,Malignant neoplasm of hypopharynx,9
C14,8,C148,"Malig neoplm of ovrlp sites of lip, oral cavity and pharynx","Malignant neoplasm of overlapping sites of lip, oral cavity and pharynx","Malignant neoplasm of other and ill-defined sites in the lip, oral cavity and pharynx",9
C15,8,C158,Malignant neoplasm of overlapping sites of esophagus,Malignant neoplasm of overlapping sites of esophagus,Malignant neoplasm of esophagus,9
C16,8,C168,Malignant neoplasm of overlapping sites of stomach,Malignant neoplasm of overlapping sites of stomach,Malignant neoplasm of stomach,9
C17,8,C178,Malignant neoplasm of overlapping sites of small intestine,Malignant neoplasm of overlapping sites of small intestine,Malignant neoplasm of small intestine,9
C18,8,C188,Malignant neoplasm of overlapping sites of colon,Malignant neoplasm of overlapping sites of colon,Malignant neoplasm of colon,9
C21,8,C218,"Malig neoplasm of ovrlp sites of rectum, anus and anal canal","Malignant neoplasm of overlapping sites of rectum, anus and anal canal",Malignant neoplasm of anus and anal canal,9
C22,8,C228,"Malignant neoplasm of liver, primary, unspecified as to type","Malignant neoplasm of liver, primary, unspecified as to type",Malignant neoplasm of liver and intrahepatic bile ducts,9
C24,8,C248,Malignant neoplasm of overlapping sites of biliary tract,Malignant neoplasm of overlapping sites of biliary tract,Malignant neoplasm of other and unspecified parts of biliary tract,9
C25,8,C258,Malignant neoplasm of overlapping sites of pancreas,Malignant neoplasm of overlapping sites of pancreas,Malignant neoplasm of pancreas,9
C31,8,C318,Malignant neoplasm of overlapping sites of accessory sinuses,Malignant neoplasm of overlapping sites of accessory sinuses,Malignant neoplasm of accessory sinuses,9
C32,8,C328,Malignant neoplasm of overlapping sites of larynx,Malignant neoplasm of overlapping sites of larynx,Malignant neoplasm of larynx,9
C38,8,C388,"Malig neoplm of ovrlp sites of heart, mediastinum and pleura","Malignant neoplasm of overlapping sites of heart, mediastinum and pleura","Malignant neoplasm of heart, mediastinum and pleura",9
C48,8,C488,Malig neoplasm of ovrlp sites of retroperiton and peritoneum,Malignant neoplasm of overlapping sites of retroperitoneum and peritoneum,Malignant neoplasm of retroperitoneum and peritoneum,9
C51,8,C518,Malignant neoplasm of overlapping sites of vulva,Malignant neoplasm of overlapping sites of vulva,Malignant neoplasm of vulva,9
C53,8,C538,Malignant neoplasm of overlapping sites of cervix uteri,Malignant neoplasm of overlapping sites of cervix uteri,Malignant neoplasm of cervix uteri,9
C54,8,C548,Malignant neoplasm of overlapping sites of corpus uteri,Malignant neoplasm of overlapping sites of corpus uteri,Malignant neoplasm of corpus uteri,9
C60,8,C608,Malignant neoplasm of overlapping sites of penis,Malignant neoplasm of overlapping sites of penis,Malignant neoplasm of penis,9
C67,8,C678,Malignant neoplasm of overlapping sites of bladder,Malignant neoplasm of overlapping sites of bladder,Malignant neoplasm of bladder,9
C68,8,C688,Malignant neoplasm of overlapping sites of urinary organs,Malignant neoplasm of overlapping sites of urinary organs,Malignant neoplasm of other and unspecified urinary organs,9
C71,8,C718,Malignant neoplasm of overlapping sites of brain,Malignant neoplasm of overlapping sites of brain,Malignant neoplasm of brain,9
C75,8,C758,"Malignant neoplasm with pluriglandular involvement, unsp","Malignant neoplasm with pluriglandular involvement, unspecified",Malignant neoplasm of other endocrine glands and related structures,9
C7A09,8,C7A098,Malignant carcinoid tumors of other sites,Malignant carcinoid tumors of other sites,Malignant carcinoid tumors of other sites,9
C77,8,C778,Sec and unsp malig neoplasm of nodes of multiple regions,Secondary and unspecified malignant neoplasm of lymph nodes of multiple regions,Secondary and unspecified malignant neoplasm of lymph nodes,9
C810,8,C8108,"Nodular lymphocyte predom Hodgkin lymphoma, nodes mult site","Nodular lymphocyte predominant Hodgkin lymphoma, lymph nodes of multiple sites",Nodular lymphocyte predominant Hodgkin lymphoma,9
C811,8,C8118,"Nodular sclerosis Hodgkin lymphoma, lymph nodes mult site","Nodular sclerosis Hodgkin lymphoma, lymph nodes of multiple sites",Nodular sclerosis Hodgkin lymphoma,9
C812,8,C8128,"Mixed cellularity Hodgkin lymphoma, lymph nodes mult site","Mixed cellularity Hodgkin lymphoma, lymph nodes of multiple sites",Mixed cellularity Hodgkin lymphoma,9
C813,8,C8138,"Lymphocyte depleted Hodgkin lymphoma, lymph nodes mult site","Lymphocyte depleted Hodgkin lymphoma, lymph nodes of multiple sites",Lymphocyte depleted Hodgkin lymphoma,9
C814,8,C8148,"Lymphocyte-rich Hodgkin lymphoma, lymph nodes mult site","Lymphocyte-rich Hodgkin lymphoma, lymph nodes of multiple sites",Lymphocyte-rich Hodgkin lymphoma,9
C817,8,C8178,"Other Hodgkin lymphoma, lymph nodes of multiple sites","Other Hodgkin lymphoma, lymph nodes of multiple sites",Other Hodgkin lymphoma,9
C819,8,C8198,"Hodgkin lymphoma, unspecified, lymph nodes of multiple sites","Hodgkin lymphoma, unspecified, lymph nodes of multiple sites","Hodgkin lymphoma, unspecified",9
C821,8,C8218,"Follicular lymphoma grade II, lymph nodes of multiple sites","Follicular lymphoma grade II, lymph nodes of multiple sites",Follicular lymphoma grade II,9
C822,8,C8228,"Follicular lymphoma grade III, unsp, lymph nodes mult site","Follicular lymphoma grade III, unspecified, lymph nodes of multiple sites","Follicular lymphoma grade III, unspecified",9
C823,8,C8238,"Follicular lymphoma grade IIIa, lymph nodes mult site","Follicular lymphoma grade IIIa, lymph nodes of multiple sites",Follicular lymphoma grade IIIa,9
C824,8,C8248,"Follicular lymphoma grade IIIb, lymph nodes mult site","Follicular lymphoma grade IIIb, lymph nodes of multiple sites",Follicular lymphoma grade IIIb,9
C825,8,C8258,"Diffuse follicle center lymphoma, lymph nodes mult site","Diffuse follicle center lymphoma, lymph nodes of multiple sites",Diffuse follicle center lymphoma,9
C826,8,C8268,"Cutaneous follicle center lymphoma, lymph nodes mult site","Cutaneous follicle center lymphoma, lymph nodes of multiple sites",Cutaneous follicle center lymphoma,9
C828,8,C8288,"Oth types of follicular lymphoma, lymph nodes mult site","Other types of follicular lymphoma, lymph nodes of multiple sites",Other types of follicular lymphoma,9
C829,8,C8298,"Follicular lymphoma, unsp, lymph nodes of multiple sites","Follicular lymphoma, unspecified, lymph nodes of multiple sites","Follicular lymphoma, unspecified",9
C830,8,C8308,"Small cell B-cell lymphoma, lymph nodes of multiple sites","Small cell B-cell lymphoma, lymph nodes of multiple sites",Small cell B-cell lymphoma,9
C831,8,C8318,"Mantle cell lymphoma, lymph nodes of multiple sites","Mantle cell lymphoma, lymph nodes of multiple sites",Mantle cell lymphoma,9
C833,8,C8338,"Diffuse large B-cell lymphoma, lymph nodes of multiple sites","Diffuse large B-cell lymphoma, lymph nodes of multiple sites",Diffuse large B-cell lymphoma,9
C835,8,C8358,"Lymphoblastic (diffuse) lymphoma, lymph nodes mult site","Lymphoblastic (diffuse) lymphoma, lymph nodes of multiple sites",Lymphoblastic (diffuse) lymphoma,9
C837,8,C8378,"Burkitt lymphoma, lymph nodes of multiple sites","Burkitt lymphoma, lymph nodes of multiple sites",Burkitt lymphoma,9
C838,8,C8388,"Other non-follicular lymphoma, lymph nodes of multiple sites","Other non-follicular lymphoma, lymph nodes of multiple sites",Other non-follicular lymphoma,9
C839,8,C8398,"Non-follic (diffuse) lymphoma, unsp, lymph nodes mult site","Non-follicular (diffuse) lymphoma, unspecified, lymph nodes of multiple sites","Non-follicular (diffuse) lymphoma, unspecified",9
C840,8,C8408,"Mycosis fungoides, lymph nodes of multiple sites","Mycosis fungoides, lymph nodes of multiple sites",Mycosis fungoides,9
C841,8,C8418,"Sezary disease, lymph nodes of multiple sites","Sezary disease, lymph nodes of multiple sites",Sezary disease,9
C844,8,C8448,"Peripheral T-cell lymphoma, not classified, nodes mult site","Peripheral T-cell lymphoma, not classified, lymph nodes of multiple sites","Peripheral T-cell lymphoma, not classified",9
C846,8,C8468,"Anaplastic large cell lymphoma, ALK-pos, nodes mult site","Anaplastic large cell lymphoma, ALK-positive, lymph nodes of multiple sites","Anaplastic large cell lymphoma, ALK-positive",9
C847,8,C8478,"Anaplastic large cell lymphoma, ALK-neg, nodes mult site","Anaplastic large cell lymphoma, ALK-negative, lymph nodes of multiple sites","Anaplastic large cell lymphoma, ALK-negative",9
C84A,8,C84A8,"Cutaneous T-cell lymphoma, unsp, lymph nodes mult site","Cutaneous T-cell lymphoma, unspecified, lymph nodes of multiple sites","Cutaneous T-cell lymphoma, unspecified",9
C84Z,8,C84Z8,"Oth mature T/NK-cell lymphomas, lymph nodes mult site","Other mature T/NK-cell lymphomas, lymph nodes of multiple sites",Other mature T/NK-cell lymphomas,9
C849,8,C8498,"Mature T/NK-cell lymphomas, unsp, lymph nodes mult site","Mature T/NK-cell lymphomas, unspecified, lymph nodes of multiple sites","Mature T/NK-cell lymphomas, unspecified",9
C851,8,C8518,"Unspecified B-cell lymphoma, lymph nodes of multiple sites","Unspecified B-cell lymphoma, lymph nodes of multiple sites",Unspecified B-cell lymphoma,9
C852,8,C8528,"Mediastinal (thymic) large B-cell lymphoma, nodes mult site","Mediastinal (thymic) large B-cell lymphoma, lymph nodes of multiple sites",Mediastinal (thymic) large B-cell lymphoma,9
C858,8,C8588,"Oth types of non-Hodgkin lymphoma, lymph nodes mult site","Other specified types of non-Hodgkin lymphoma, lymph nodes of multiple sites",Other specified types of non-Hodgkin lymphoma,9
C859,8,C8598,"Non-Hodgkin lymphoma, unsp, lymph nodes of multiple sites","Non-Hodgkin lymphoma, unspecified, lymph nodes of multiple sites","Non-Hodgkin lymphoma, unspecified",9
C88,8,C888,Other malignant immunoproliferative diseases,Other malignant immunoproliferative diseases,Malignant immunoproliferative diseases and certain other B-cell lymphomas,9
D000,8,D0008,Carcinoma in situ of pharynx,Carcinoma in situ of pharynx,"Carcinoma in situ of lip, oral cavity and pharynx",9
D12,8,D128,Benign neoplasm of rectum,Benign neoplasm of rectum,"Benign neoplasm of colon, rectum, anus and anal canal",9
D3A09,8,D3A098,Benign carcinoid tumors of other sites,Benign carcinoid tumors of other sites,Benign carcinoid tumors of other sites,9
D43,8,D438,Neoplasm of uncertain behavior of prt central nervous system,Neoplasm of uncertain behavior of other specified parts of central nervous system,Neoplasm of uncertain behavior of brain and central nervous system,9
D50,8,D508,Other iron deficiency anemias,Other iron deficiency anemias,Iron deficiency anemia,9
D51,8,D518,Other vitamin B12 deficiency anemias,Other vitamin B12 deficiency anemias,Vitamin B12 deficiency anemia,9
D52,8,D528,Other folate deficiency anemias,Other folate deficiency anemias,Folate deficiency anemia,9
D53,8,D538,Other specified nutritional anemias,Other specified nutritional anemias,Other nutritional anemias,9
D55,8,D558,Other anemias due to enzyme disorders,Other anemias due to enzyme disorders,Anemia due to enzyme disorders,9
D56,8,D568,Other thalassemias,Other thalassemias,Thalassemia,9
D58,8,D588,Other specified hereditary hemolytic anemias,Other specified hereditary hemolytic anemias,Other hereditary hemolytic anemias,9
D59,8,D598,Other acquired hemolytic anemias,Other acquired hemolytic anemias,Acquired hemolytic anemia,9
D60,8,D608,Other acquired pure red cell aplasias,Other acquired pure red cell aplasias,Acquired pure red cell aplasia [erythroblastopenia],9
D6181,8,D61818,Other pancytopenia,Other pancytopenia,Pancytopenia,9
E64,8,E648,Sequelae of other nutritional deficiencies,Sequelae of other nutritional deficiencies,Sequelae of malnutrition and other nutritional deficiencies,9
D63,8,D638,Anemia in other chronic diseases classified elsewhere,Anemia in other chronic diseases classified elsewhere,Anemia in chronic diseases classified elsewhere,9
D6831,8,D68318,"Oth hemorrhagic disord d/t intrns circ anticoag,antib,inhib","Other hemorrhagic disorder due to intrinsic circulating anticoagulants, antibodies, or inhibitors","Hemorrhagic disorder due to intrinsic circulating anticoagulants, antibodies, or inhibitors",9
D70,8,D708,Other neutropenia,Other neutropenia,Neutropenia,9
D7281,8,D72818,Other decreased white blood cell count,Other decreased white blood cell count,Decreased white blood cell count,9
D7282,8,D72828,Other elevated white blood cell count,Other elevated white blood cell count,Elevated white blood cell count,9
D74,8,D748,Other methemoglobinemias,Other methemoglobinemias,Methemoglobinemia,9
D80,8,D808,Other immunodeficiencies with predominantly antibody defects,Other immunodeficiencies with predominantly antibody defects,Immunodeficiency with predominantly antibody defects,9
D8181,8,D81818,Other biotin-dependent carboxylase deficiency,Other biotin-dependent carboxylase deficiency,Biotin-dependent carboxylase deficiency,9
D82,8,D828,Immunodeficiency associated with oth major defects,Immunodeficiency associated with other specified major defects,Immunodeficiency associated with other major defects,9
D83,8,D838,Other common variable immunodeficiencies,Other common variable immunodeficiencies,Common variable immunodeficiency,9
D84,8,D848,Other specified immunodeficiencies,Other specified immunodeficiencies,Other immunodeficiencies,9
E01,8,E018,Oth iodine-deficiency related thyroid disord and allied cond,Other iodine-deficiency related thyroid disorders and allied conditions,Iodine-deficiency related thyroid disorders and allied conditions,9
E03,8,E038,Other specified hypothyroidism,Other specified hypothyroidism,Other hypothyroidism,9
E04,8,E048,Other specified nontoxic goiter,Other specified nontoxic goiter,Other nontoxic goiter,9
E0861,8,E08618,Diabetes due to underlying condition w oth diabetic arthrop,Diabetes mellitus due to underlying condition with other diabetic arthropathy,Diabetes mellitus due to underlying condition with diabetic arthropathy,9
E0862,8,E08628,Diabetes due to underlying condition w oth skin comp,Diabetes mellitus due to underlying condition with other skin complications,Diabetes mellitus due to underlying condition with skin complications,9
E0863,8,E08638,Diabetes due to underlying condition w oth oral comp,Diabetes mellitus due to underlying condition with other oral complications,Diabetes mellitus due to underlying condition with oral complications,9
E0961,8,E09618,Drug/chem diabetes mellitus w oth diabetic arthropathy,Drug or chemical induced diabetes mellitus with other diabetic arthropathy,Drug or chemical induced diabetes mellitus with diabetic arthropathy,9
E0962,8,E09628,Drug/chem diabetes mellitus w oth skin complications,Drug or chemical induced diabetes mellitus with other skin complications,Drug or chemical induced diabetes mellitus with skin complications,9
E0963,8,E09638,Drug/chem diabetes mellitus w oth oral complications,Drug or chemical induced diabetes mellitus with other oral complications,Drug or chemical induced diabetes mellitus with oral complications,9
E1061,8,E10618,Type 1 diabetes mellitus with other diabetic arthropathy,Type 1 diabetes mellitus with other diabetic arthropathy,Type 1 diabetes mellitus with diabetic arthropathy,9
E1062,8,E10628,Type 1 diabetes mellitus with other skin complications,Type 1 diabetes mellitus with other skin complications,Type 1 diabetes mellitus with skin complications,9
E1063,8,E10638,Type 1 diabetes mellitus with other oral complications,Type 1 diabetes mellitus with other oral complications,Type 1 diabetes mellitus with oral complications,9
E1161,8,E11618,Type 2 diabetes mellitus with other diabetic arthropathy,Type 2 diabetes mellitus with other diabetic arthropathy,Type 2 diabetes mellitus with diabetic arthropathy,9
E1162,8,E11628,Type 2 diabetes mellitus with other skin complications,Type 2 diabetes mellitus with other skin complications,Type 2 diabetes mellitus with skin complications,9
E1163,8,E11638,Type 2 diabetes mellitus with other oral complications,Type 2 diabetes mellitus with other oral complications,Type 2 diabetes mellitus with oral complications,9
E1361,8,E13618,Oth diabetes mellitus with other diabetic arthropathy,Other specified diabetes mellitus with other diabetic arthropathy,Other specified diabetes mellitus with diabetic arthropathy,9
E1362,8,E13628,Oth diabetes mellitus with other skin complications,Other specified diabetes mellitus with other skin complications,Other specified diabetes mellitus with skin complications,9
E1363,8,E13638,Oth diabetes mellitus with other oral complications,Other specified diabetes mellitus with other oral complications,Other specified diabetes mellitus with oral complications,9
E16,8,E168,Other specified disorders of pancreatic internal secretion,Other specified disorders of pancreatic internal secretion,Other disorders of pancreatic internal secretion,9
E20,8,E208,Other hypoparathyroidism,Other hypoparathyroidism,Hypoparathyroidism,9
E22,8,E228,Other hyperfunction of pituitary gland,Other hyperfunction of pituitary gland,Hyperfunction of pituitary gland,9
E24,8,E248,Other Cushing's syndrome,Other Cushing's syndrome,Cushing's syndrome,9
E25,8,E258,Other adrenogenital disorders,Other adrenogenital disorders,Adrenogenital disorders,9
E29,8,E298,Other testicular dysfunction,Other testicular dysfunction,Testicular dysfunction,9
E30,8,E308,Other disorders of puberty,Other disorders of puberty,"Disorders of puberty, not elsewhere classified",9
E32,8,E328,Other diseases of thymus,Other diseases of thymus,Diseases of thymus,9
E50,8,E508,Other manifestations of vitamin A deficiency,Other manifestations of vitamin A deficiency,Vitamin A deficiency,9
E53,8,E538,Deficiency of other specified B group vitamins,Deficiency of other specified B group vitamins,Deficiency of other B group vitamins,9
E56,8,E568,Deficiency of other vitamins,Deficiency of other vitamins,Other vitamin deficiencies,9
E61,8,E618,Deficiency of other specified nutrient elements,Deficiency of other specified nutrient elements,Deficiency of other nutrient elements,9
E63,8,E638,Other specified nutritional deficiencies,Other specified nutritional deficiencies,Other nutritional deficiencies,9
E67,8,E678,Other specified hyperalimentation,Other specified hyperalimentation,Other hyperalimentation,9
E7032,8,E70328,Other oculocutaneous albinism,Other oculocutaneous albinism,Oculocutaneous albinism,9
E7033,8,E70338,Other albinism with hematologic abnormality,Other albinism with hematologic abnormality,Albinism with hematologic abnormality,9
E7111,8,E71118,Other branched-chain organic acidurias,Other branched-chain organic acidurias,Branched-chain organic acidurias,9
E7112,8,E71128,Other disorders of propionate metabolism,Other disorders of propionate metabolism,Disorders of propionate metabolism,9
E7131,8,E71318,Other disorders of fatty-acid oxidation,Other disorders of fatty-acid oxidation,Disorders of fatty-acid oxidation,9
E7144,8,E71448,Other secondary carnitine deficiency,Other secondary carnitine deficiency,Other secondary carnitine deficiency,9
E7151,8,E71518,Other disorders of peroxisome biogenesis,Other disorders of peroxisome biogenesis,Disorders of peroxisome biogenesis,9
E7152,8,E71528,Other X-linked adrenoleukodystrophy,Other X-linked adrenoleukodystrophy,X-linked adrenoleukodystrophy,9
E7154,8,E71548,Other peroxisomal disorders,Other peroxisomal disorders,Other peroxisomal disorders,9
E73,8,E738,Other lactose intolerance,Other lactose intolerance,Lactose intolerance,9
E7524,8,E75248,Other Niemann-Pick disease,Other Niemann-Pick disease,Niemann-Pick disease,9
E77,8,E778,Other disorders of glycoprotein metabolism,Other disorders of glycoprotein metabolism,Disorders of glycoprotein metabolism,9
E79,8,E798,Other disorders of purine and pyrimidine metabolism,Other disorders of purine and pyrimidine metabolism,Disorders of purine and pyrimidine metabolism,9
E8311,8,E83118,Other hemochromatosis,Other hemochromatosis,Hemochromatosis,9
F1018,8,F10188,Alcohol abuse with other alcohol-induced disorder,Alcohol abuse with other alcohol-induced disorder,Alcohol abuse with other alcohol-induced disorders,9
F1028,8,F10288,Alcohol dependence with other alcohol-induced disorder,Alcohol dependence with other alcohol-induced disorder,Alcohol dependence with other alcohol-induced disorders,9
F1098,8,F10988,"Alcohol use, unspecified with other alcohol-induced disorder","Alcohol use, unspecified with other alcohol-induced disorder","Alcohol use, unspecified with other alcohol-induced disorders",9
F1118,8,F11188,Opioid abuse with other opioid-induced disorder,Opioid abuse with other opioid-induced disorder,Opioid abuse with other opioid-induced disorder,9
F1128,8,F11288,Opioid dependence with other opioid-induced disorder,Opioid dependence with other opioid-induced disorder,Opioid dependence with other opioid-induced disorder,9
F1198,8,F11988,"Opioid use, unspecified with other opioid-induced disorder","Opioid use, unspecified with other opioid-induced disorder","Opioid use, unspecified with other specified opioid-induced disorder",9
F1218,8,F12188,Cannabis abuse with other cannabis-induced disorder,Cannabis abuse with other cannabis-induced disorder,Cannabis abuse with other cannabis-induced disorder,9
F1228,8,F12288,Cannabis dependence with other cannabis-induced disorder,Cannabis dependence with other cannabis-induced disorder,Cannabis dependence with other cannabis-induced disorder,9
F1298,8,F12988,"Cannabis use, unsp with other cannabis-induced disorder","Cannabis use, unspecified with other cannabis-induced disorder","Cannabis use, unspecified with other cannabis-induced disorder",9
F1318,8,F13188,"Sedative, hypnotic or anxiolytic abuse w oth disorder","Sedative, hypnotic or anxiolytic abuse with other sedative, hypnotic or anxiolytic-induced disorder","Sedative, hypnotic or anxiolytic abuse with other sedative, hypnotic or anxiolytic-induced disorders",9
F1328,8,F13288,"Sedative, hypnotic or anxiolytic dependence w oth disorder","Sedative, hypnotic or anxiolytic dependence with other sedative, hypnotic or anxiolytic-induced disorder","Sedative, hypnotic or anxiolytic dependence with other sedative, hypnotic or anxiolytic-induced disorders",9
F1398,8,F13988,"Sedative, hypnotic or anxiolytic use, unsp w oth disorder","Sedative, hypnotic or anxiolytic use, unspecified with other sedative, hypnotic or anxiolytic-induced disorder","Sedative, hypnotic or anxiolytic use, unspecified with other sedative, hypnotic or anxiolytic-induced disorders",9
F1418,8,F14188,Cocaine abuse with other cocaine-induced disorder,Cocaine abuse with other cocaine-induced disorder,Cocaine abuse with other cocaine-induced disorder,9
F1428,8,F14288,Cocaine dependence with other cocaine-induced disorder,Cocaine dependence with other cocaine-induced disorder,Cocaine dependence with other cocaine-induced disorder,9
F1498,8,F14988,"Cocaine use, unspecified with other cocaine-induced disorder","Cocaine use, unspecified with other cocaine-induced disorder","Cocaine use, unspecified with other specified cocaine-induced disorder",9
F1518,8,F15188,Other stimulant abuse with other stimulant-induced disorder,Other stimulant abuse with other stimulant-induced disorder,Other stimulant abuse with other stimulant-induced disorder,9
F1528,8,F15288,Oth stimulant dependence with oth stimulant-induced disorder,Other stimulant dependence with other stimulant-induced disorder,Other stimulant dependence with other stimulant-induced disorder,9
F1598,8,F15988,"Oth stimulant use, unsp with oth stimulant-induced disorder","Other stimulant use, unspecified with other stimulant-induced disorder","Other stimulant use, unspecified with other stimulant-induced disorder",9
F1618,8,F16188,Hallucinogen abuse with other hallucinogen-induced disorder,Hallucinogen abuse with other hallucinogen-induced disorder,Hallucinogen abuse with other hallucinogen-induced disorder,9
F1628,8,F16288,Hallucinogen dependence w oth hallucinogen-induced disorder,Hallucinogen dependence with other hallucinogen-induced disorder,Hallucinogen dependence with other hallucinogen-induced disorder,9
F1698,8,F16988,"Hallucinogen use, unsp w oth hallucinogen-induced disorder","Hallucinogen use, unspecified with other hallucinogen-induced disorder","Hallucinogen use, unspecified with other specified hallucinogen-induced disorder",9
F1720,8,F17208,"Nicotine dependence, unsp, w oth nicotine-induced disorders","Nicotine dependence, unspecified, with other nicotine-induced disorders","Nicotine dependence, unspecified",9
F1721,8,F17218,"Nicotine dependence, cigarettes, w oth disorders","Nicotine dependence, cigarettes, with other nicotine-induced disorders","Nicotine dependence, cigarettes",9
F1722,8,F17228,"Nicotine dependence, chewing tobacco, w oth disorders","Nicotine dependence, chewing tobacco, with other nicotine-induced disorders","Nicotine dependence, chewing tobacco",9
A774,9,A7749,Other ehrlichiosis,Other ehrlichiosis,Ehrlichiosis,9
F1729,8,F17298,"Nicotine dependence, oth tobacco product, w oth disorders","Nicotine dependence, other tobacco product, with other nicotine-induced disorders","Nicotine dependence, other tobacco product",9
F1818,8,F18188,Inhalant abuse with other inhalant-induced disorder,Inhalant abuse with other inhalant-induced disorder,Inhalant abuse with other inhalant-induced disorders,9
F1828,8,F18288,Inhalant dependence with other inhalant-induced disorder,Inhalant dependence with other inhalant-induced disorder,Inhalant dependence with other inhalant-induced disorders,9
F1898,8,F18988,"Inhalant use, unsp with other inhalant-induced disorder","Inhalant use, unspecified with other inhalant-induced disorder","Inhalant use, unspecified with other inhalant-induced disorders",9
F1918,8,F19188,Oth psychoactive substance abuse w oth disorder,Other psychoactive substance abuse with other psychoactive substance-induced disorder,Other psychoactive substance abuse with other psychoactive substance-induced disorders,9
F1928,8,F19288,Oth psychoactive substance dependence w oth disorder,Other psychoactive substance dependence with other psychoactive substance-induced disorder,Other psychoactive substance dependence with other psychoactive substance-induced disorders,9
F1998,8,F19988,"Oth psychoactive substance use, unsp w oth disorder","Other psychoactive substance use, unspecified with other psychoactive substance-induced disorder","Other psychoactive substance use, unspecified with other psychoactive substance-induced disorders",9
F25,8,F258,Other schizoaffective disorders,Other schizoaffective disorders,Schizoaffective disorders,9
F317,8,F3178,"Bipolar disorder, in full remis, most recent episode mixed","Bipolar disorder, in full remission, most recent episode mixed","Bipolar disorder, currently in remission",9
F4021,8,F40218,Other animal type phobia,Other animal type phobia,Animal type phobia,9
F4022,8,F40228,Other natural environment type phobia,Other natural environment type phobia,Natural environment type phobia,9
F4024,8,F40248,Other situational type phobia,Other situational type phobia,Situational type phobia,9
F4029,8,F40298,Other specified phobia,Other specified phobia,Other specified phobia,9
F41,8,F418,Other specified anxiety disorders,Other specified anxiety disorders,Other anxiety disorders,9
F42,8,F428,Other obsessive-compulsive disorder,Other obsessive-compulsive disorder,Obsessive-compulsive disorder,9
F48,8,F488,Other specified nonpsychotic mental disorders,Other specified nonpsychotic mental disorders,Other nonpsychotic mental disorders,9
F55,8,F558,Abuse of other non-psychoactive substances,Abuse of other non-psychoactive substances,Abuse of non-psychoactive substances,9
F64,8,F648,Other gender identity disorders,Other gender identity disorders,Gender identity disorders,9
F84,8,F848,Other pervasive developmental disorders,Other pervasive developmental disorders,Pervasive developmental disorders,9
F90,8,F908,"Attention-deficit hyperactivity disorder, other type","Attention-deficit hyperactivity disorder, other type",Attention-deficit hyperactivity disorders,9
F91,8,F918,Other conduct disorders,Other conduct disorders,Conduct disorders,9
F93,8,F938,Other childhood emotional disorders,Other childhood emotional disorders,Emotional disorders with onset specific to childhood,9
F94,8,F948,Other childhood disorders of social functioning,Other childhood disorders of social functioning,Disorders of social functioning with onset specific to childhood and adolescence,9
F95,8,F958,Other tic disorders,Other tic disorders,Tic disorder,9
G00,8,G008,Other bacterial meningitis,Other bacterial meningitis,"Bacterial meningitis, not elsewhere classified",9
G03,8,G038,Meningitis due to other specified causes,Meningitis due to other specified causes,Meningitis due to other and unspecified causes,9
G11,8,G118,Other hereditary ataxias,Other hereditary ataxias,Hereditary ataxia,9
G13,8,G138,Systemic atrophy aff cnsl in oth diseases classd elswhr,Systemic atrophy primarily affecting central nervous system in other diseases classified elsewhere,Systemic atrophies primarily affecting central nervous system in diseases classified elsewhere,9
G23,8,G238,Other specified degenerative diseases of basal ganglia,Other specified degenerative diseases of basal ganglia,Other degenerative diseases of basal ganglia,9
G30,8,G308,Other Alzheimer's disease,Other Alzheimer's disease,Alzheimer's disease,9
G36,8,G368,Other specified acute disseminated demyelination,Other specified acute disseminated demyelination,Other acute disseminated demyelination,9
G37,8,G378,Oth demyelinating diseases of central nervous system,Other specified demyelinating diseases of central nervous system,Other demyelinating diseases of central nervous system,9
G45,8,G458,Oth transient cerebral ischemic attacks and related synd,Other transient cerebral ischemic attacks and related syndromes,Transient cerebral ischemic attacks and related syndromes,9
G46,8,G468,Oth vascular syndromes of brain in cerebrovascular diseases,Other vascular syndromes of brain in cerebrovascular diseases,Vascular syndromes of brain in cerebrovascular diseases,9
G50,8,G508,Other disorders of trigeminal nerve,Other disorders of trigeminal nerve,Disorders of trigeminal nerve,9
G51,8,G518,Other disorders of facial nerve,Other disorders of facial nerve,Facial nerve disorders,9
G52,8,G528,Disorders of other specified cranial nerves,Disorders of other specified cranial nerves,Disorders of other cranial nerves,9
G54,8,G548,Other nerve root and plexus disorders,Other nerve root and plexus disorders,Nerve root and plexus disorders,9
A00,9,A009,"Cholera, unspecified","Cholera, unspecified",Cholera,9
A010,9,A0109,Typhoid fever with other complications,Typhoid fever with other complications,Typhoid fever,9
A022,9,A0229,Salmonella with other localized infection,Salmonella with other localized infection,Localized salmonella infections,9
A03,9,A039,"Shigellosis, unspecified","Shigellosis, unspecified",Shigellosis,9
A05,9,A059,"Bacterial foodborne intoxication, unspecified","Bacterial foodborne intoxication, unspecified","Other bacterial foodborne intoxications, not elsewhere classified",9
A068,9,A0689,Other amebic infections,Other amebic infections,Amebic infection of other sites,9
A07,9,A079,"Protozoal intestinal disease, unspecified","Protozoal intestinal disease, unspecified",Other protozoal intestinal diseases,9
A081,9,A0819,Acute gastroenteropathy due to other small round viruses,Acute gastroenteropathy due to other small round viruses,Acute gastroenteropathy due to Norwalk agent and other small round viruses,9
A083,9,A0839,Other viral enteritis,Other viral enteritis,Other viral enteritis,9
A15,9,A159,Respiratory tuberculosis unspecified,Respiratory tuberculosis unspecified,Respiratory tuberculosis,9
A178,9,A1789,Other tuberculosis of nervous system,Other tuberculosis of nervous system,Other tuberculosis of nervous system,9
A180,9,A1809,Other musculoskeletal tuberculosis,Other musculoskeletal tuberculosis,Tuberculosis of bones and joints,9
A183,9,A1839,Retroperitoneal tuberculosis,Retroperitoneal tuberculosis,"Tuberculosis of intestines, peritoneum and mesenteric glands",9
A185,9,A1859,Other tuberculosis of eye,Other tuberculosis of eye,Tuberculosis of eye,9
A188,9,A1889,Tuberculosis of other sites,Tuberculosis of other sites,Tuberculosis of other specified organs,9
A19,9,A199,"Miliary tuberculosis, unspecified","Miliary tuberculosis, unspecified",Miliary tuberculosis,9
A20,9,A209,"Plague, unspecified","Plague, unspecified",Plague,9
A21,9,A219,"Tularemia, unspecified","Tularemia, unspecified",Tularemia,9
A22,9,A229,"Anthrax, unspecified","Anthrax, unspecified",Anthrax,9
A23,9,A239,"Brucellosis, unspecified","Brucellosis, unspecified",Brucellosis,9
A24,9,A249,"Melioidosis, unspecified","Melioidosis, unspecified",Glanders and melioidosis,9
A25,9,A259,"Rat-bite fever, unspecified","Rat-bite fever, unspecified",Rat-bite fevers,9
A26,9,A269,"Erysipeloid, unspecified","Erysipeloid, unspecified",Erysipeloid,9
A278,9,A2789,Other forms of leptospirosis,Other forms of leptospirosis,Other forms of leptospirosis,9
A28,9,A289,"Zoonotic bacterial disease, unspecified","Zoonotic bacterial disease, unspecified","Other zoonotic bacterial diseases, not elsewhere classified",9
A30,9,A309,"Leprosy, unspecified","Leprosy, unspecified",Leprosy [Hansen's disease],9
A31,9,A319,"Mycobacterial infection, unspecified","Mycobacterial infection, unspecified",Infection due to other mycobacteria,9
A328,9,A3289,Other forms of listeriosis,Other forms of listeriosis,Other forms of listeriosis,9
A368,9,A3689,Other diphtheritic complications,Other diphtheritic complications,Other diphtheria,9
A38,9,A389,"Scarlet fever, uncomplicated","Scarlet fever, uncomplicated",Scarlet fever,9
A398,9,A3989,Other meningococcal infections,Other meningococcal infections,Other meningococcal infections,9
A40,9,A409,"Streptococcal sepsis, unspecified","Streptococcal sepsis, unspecified",Streptococcal sepsis,9
A415,9,A4159,Other Gram-negative sepsis,Other Gram-negative sepsis,Sepsis due to other Gram-negative organisms,9
A418,9,A4189,Other specified sepsis,Other specified sepsis,Other specified sepsis,9
A428,9,A4289,Other forms of actinomycosis,Other forms of actinomycosis,Other forms of actinomycosis,9
A43,9,A439,"Nocardiosis, unspecified","Nocardiosis, unspecified",Nocardiosis,9
A44,9,A449,"Bartonellosis, unspecified","Bartonellosis, unspecified",Bartonellosis,9
A500,9,A5009,"Other early congenital syphilis, symptomatic","Other early congenital syphilis, symptomatic","Early congenital syphilis, symptomatic",9
A503,9,A5039,Other late congenital syphilitic oculopathy,Other late congenital syphilitic oculopathy,Late congenital syphilitic oculopathy,9
A504,9,A5049,Other late congenital neurosyphilis,Other late congenital neurosyphilis,Late congenital neurosyphilis [juvenile neurosyphilis],9
A505,9,A5059,"Other late congenital syphilis, symptomatic","Other late congenital syphilis, symptomatic","Other late congenital syphilis, symptomatic",9
A513,9,A5139,Other secondary syphilis of skin,Other secondary syphilis of skin,Secondary syphilis of skin and mucous membranes,9
A514,9,A5149,Other secondary syphilitic conditions,Other secondary syphilitic conditions,Other secondary syphilis,9
A520,9,A5209,Other cardiovascular syphilis,Other cardiovascular syphilis,Cardiovascular and cerebrovascular syphilis,9
A521,9,A5219,Other symptomatic neurosyphilis,Other symptomatic neurosyphilis,Symptomatic neurosyphilis,9
A527,9,A5279,Other symptomatic late syphilis,Other symptomatic late syphilis,Other symptomatic late syphilis,9
A53,9,A539,"Syphilis, unspecified","Syphilis, unspecified",Other and unspecified syphilis,9
A540,9,A5409,Other gonococcal infection of lower genitourinary tract,Other gonococcal infection of lower genitourinary tract,Gonococcal infection of lower genitourinary tract without periurethral or accessory gland abscess,9
A542,9,A5429,Other gonococcal genitourinary infections,Other gonococcal genitourinary infections,Gonococcal pelviperitonitis and other gonococcal genitourinary infection,9
A543,9,A5439,Other gonococcal eye infection,Other gonococcal eye infection,Gonococcal infection of eye,9
A544,9,A5449,Gonococcal infection of other musculoskeletal tissue,Gonococcal infection of other musculoskeletal tissue,Gonococcal infection of musculoskeletal system,9
A548,9,A5489,Other gonococcal infections,Other gonococcal infections,Other gonococcal infections,9
A560,9,A5609,Other chlamydial infection of lower genitourinary tract,Other chlamydial infection of lower genitourinary tract,Chlamydial infection of lower genitourinary tract,9
A561,9,A5619,Other chlamydial genitourinary infection,Other chlamydial genitourinary infection,Chlamydial infection of pelviperitoneum and other genitourinary organs,9
A590,9,A5909,Other urogenital trichomoniasis,Other urogenital trichomoniasis,Urogenital trichomoniasis,9
A600,9,A6009,Herpesviral infection of other urogenital tract,Herpesviral infection of other urogenital tract,Herpesviral infection of genitalia and urogenital tract,9
A66,9,A669,"Yaws, unspecified","Yaws, unspecified",Yaws,9
A67,9,A679,"Pinta, unspecified","Pinta, unspecified",Pinta [carate],9
A68,9,A689,"Relapsing fever, unspecified","Relapsing fever, unspecified",Relapsing fevers,9
A692,9,A6929,Other conditions associated with Lyme disease,Other conditions associated with Lyme disease,Lyme disease,9
A71,9,A719,"Trachoma, unspecified","Trachoma, unspecified",Trachoma,9
A748,9,A7489,Other chlamydial diseases,Other chlamydial diseases,Other chlamydial diseases,9
A798,9,A7989,Other specified rickettsioses,Other specified rickettsioses,Other specified rickettsioses,9
A803,9,A8039,Other acute paralytic poliomyelitis,Other acute paralytic poliomyelitis,"Acute paralytic poliomyelitis, other and unspecified",9
A810,9,A8109,Other Creutzfeldt-Jakob disease,Other Creutzfeldt-Jakob disease,Creutzfeldt-Jakob disease,9
A818,9,A8189,Other atypical virus infections of central nervous system,Other atypical virus infections of central nervous system,Other atypical virus infections of central nervous system,9
A82,9,A829,"Rabies, unspecified","Rabies, unspecified",Rabies,9
A83,9,A839,"Mosquito-borne viral encephalitis, unspecified","Mosquito-borne viral encephalitis, unspecified",Mosquito-borne viral encephalitis,9
A84,9,A849,"Tick-borne viral encephalitis, unspecified","Tick-borne viral encephalitis, unspecified",Tick-borne viral encephalitis,9
A87,9,A879,"Viral meningitis, unspecified","Viral meningitis, unspecified",Viral meningitis,9
A923,9,A9239,West Nile virus infection with other complications,West Nile virus infection with other complications,West Nile virus infection,9
A95,9,A959,"Yellow fever, unspecified","Yellow fever, unspecified",Yellow fever,9
A96,9,A969,"Arenaviral hemorrhagic fever, unspecified","Arenaviral hemorrhagic fever, unspecified",Arenaviral hemorrhagic fever,9
B005,9,B0059,Other herpesviral disease of eye,Other herpesviral disease of eye,Herpesviral ocular disease,9
B008,9,B0089,Other herpesviral infection,Other herpesviral infection,Other forms of herpesviral infections,9
B018,9,B0189,Other varicella complications,Other varicella complications,Varicella with other complications,9
B022,9,B0229,Other postherpetic nervous system involvement,Other postherpetic nervous system involvement,Zoster with other nervous system involvement,9
B023,9,B0239,Other herpes zoster eye disease,Other herpes zoster eye disease,Zoster ocular disease,9
B058,9,B0589,Other measles complications,Other measles complications,Measles with other complications,9
B060,9,B0609,Other neurological complications of rubella,Other neurological complications of rubella,Rubella with neurological complications,9
B068,9,B0689,Other rubella complications,Other rubella complications,Rubella with other complications,9
B07,9,B079,"Viral wart, unspecified","Viral wart, unspecified",Viral warts,9
B086,9,B0869,Other parapoxvirus infections,Other parapoxvirus infections,Parapoxvirus infections,9
B087,9,B0879,Other yatapoxvirus infections,Other yatapoxvirus infections,Yatapoxvirus infections,9
B100,9,B1009,Other human herpesvirus encephalitis,Other human herpesvirus encephalitis,Other human herpesvirus encephalitis,9
B108,9,B1089,Other human herpesvirus infection,Other human herpesvirus infection,Other human herpesvirus infection,9
B15,9,B159,Hepatitis A without hepatic coma,Hepatitis A without hepatic coma,Acute hepatitis A,9
B16,9,B169,Acute hepatitis B w/o delta-agent and without hepatic coma,Acute hepatitis B without delta-agent and without hepatic coma,Acute hepatitis B,9
B18,9,B189,"Chronic viral hepatitis, unspecified","Chronic viral hepatitis, unspecified",Chronic viral hepatitis,9
B25,9,B259,"Cytomegaloviral disease, unspecified","Cytomegaloviral disease, unspecified",Cytomegaloviral disease,9
B268,9,B2689,Other mumps complications,Other mumps complications,Mumps with other complications,9
B270,9,B2709,Gammaherpesviral mononucleosis with other complications,Gammaherpesviral mononucleosis with other complications,Gammaherpesviral mononucleosis,9
B271,9,B2719,Cytomegaloviral mononucleosis with other complication,Cytomegaloviral mononucleosis with other complication,Cytomegaloviral mononucleosis,9
B278,9,B2789,Other infectious mononucleosis with other complication,Other infectious mononucleosis with other complication,Other infectious mononucleosis,9
B279,9,B2799,"Infectious mononucleosis, unsp with other complication","Infectious mononucleosis, unspecified with other complication","Infectious mononucleosis, unspecified",9
B30,9,B309,"Viral conjunctivitis, unspecified","Viral conjunctivitis, unspecified",Viral conjunctivitis,9
B34,9,B349,"Viral infection, unspecified","Viral infection, unspecified",Viral infection of unspecified site,9
B35,9,B359,"Dermatophytosis, unspecified","Dermatophytosis, unspecified",Dermatophytosis,9
B36,9,B369,"Superficial mycosis, unspecified","Superficial mycosis, unspecified",Other superficial mycoses,9
B374,9,B3749,Other urogenital candidiasis,Other urogenital candidiasis,Candidiasis of other urogenital sites,9
B378,9,B3789,Other sites of candidiasis,Other sites of candidiasis,Candidiasis of other sites,9
B388,9,B3889,Other forms of coccidioidomycosis,Other forms of coccidioidomycosis,Other forms of coccidioidomycosis,9
B39,9,B399,"Histoplasmosis, unspecified","Histoplasmosis, unspecified",Histoplasmosis,9
B408,9,B4089,Other forms of blastomycosis,Other forms of blastomycosis,Other forms of blastomycosis,9
B41,9,B419,"Paracoccidioidomycosis, unspecified","Paracoccidioidomycosis, unspecified",Paracoccidioidomycosis,9
B428,9,B4289,Other forms of sporotrichosis,Other forms of sporotrichosis,Other forms of sporotrichosis,9
B43,9,B439,"Chromomycosis, unspecified","Chromomycosis, unspecified",Chromomycosis and pheomycotic abscess,9
B448,9,B4489,Other forms of aspergillosis,Other forms of aspergillosis,Other forms of aspergillosis,9
B45,9,B459,"Cryptococcosis, unspecified","Cryptococcosis, unspecified",Cryptococcosis,9
B46,9,B469,"Zygomycosis, unspecified","Zygomycosis, unspecified",Zygomycosis,9
B47,9,B479,"Mycetoma, unspecified","Mycetoma, unspecified",Mycetoma,9
B50,9,B509,"Plasmodium falciparum malaria, unspecified","Plasmodium falciparum malaria, unspecified",Plasmodium falciparum malaria,9
B51,9,B519,Plasmodium vivax malaria without complication,Plasmodium vivax malaria without complication,Plasmodium vivax malaria,9
B52,9,B529,Plasmodium malariae malaria without complication,Plasmodium malariae malaria without complication,Plasmodium malariae malaria,9
B55,9,B559,"Leishmaniasis, unspecified","Leishmaniasis, unspecified",Leishmaniasis,9
B56,9,B569,"African trypanosomiasis, unspecified","African trypanosomiasis, unspecified",African trypanosomiasis,9
B573,9,B5739,Other digestive system involvement in Chagas' disease,Other digestive system involvement in Chagas' disease,Chagas' disease (chronic) with digestive system involvement,9
B574,9,B5749,Other nervous system involvement in Chagas' disease,Other nervous system involvement in Chagas' disease,Chagas' disease (chronic) with nervous system involvement,9
B580,9,B5809,Other toxoplasma oculopathy,Other toxoplasma oculopathy,Toxoplasma oculopathy,9
B588,9,B5889,Toxoplasmosis with other organ involvement,Toxoplasmosis with other organ involvement,Toxoplasmosis with other organ involvement,9
B601,9,B6019,Other acanthamebic disease,Other acanthamebic disease,Acanthamebiasis,9
B65,9,B659,"Schistosomiasis, unspecified","Schistosomiasis, unspecified",Schistosomiasis [bilharziasis],9
B66,9,B669,"Fluke infection, unspecified","Fluke infection, unspecified",Other fluke infections,9
B673,9,B6739,"Echinococcus granulosus infection, other sites","Echinococcus granulosus infection, other sites","Echinococcus granulosus infection, other and multiple sites",9
B676,9,B6769,"Echinococcus multilocularis infection, other sites","Echinococcus multilocularis infection, other sites","Echinococcus multilocularis infection, other and multiple sites",9
B679,9,B6799,Other echinococcosis,Other echinococcosis,"Echinococcosis, other and unspecified",9
B68,9,B689,"Taeniasis, unspecified","Taeniasis, unspecified",Taeniasis,9
B698,9,B6989,Cysticercosis of other sites,Cysticercosis of other sites,Cysticercosis of other sites,9
B71,9,B719,"Cestode infection, unspecified","Cestode infection, unspecified",Other cestode infections,9
B730,9,B7309,Onchocerciasis with other eye involvement,Onchocerciasis with other eye involvement,Onchocerciasis with eye disease,9
B74,9,B749,"Filariasis, unspecified","Filariasis, unspecified",Filariasis,9
B76,9,B769,"Hookworm disease, unspecified","Hookworm disease, unspecified",Hookworm diseases,9
B778,9,B7789,Ascariasis with other complications,Ascariasis with other complications,Ascariasis with other complications,9
B78,9,B789,"Strongyloidiasis, unspecified","Strongyloidiasis, unspecified",Strongyloidiasis,9
B82,9,B829,"Intestinal parasitism, unspecified","Intestinal parasitism, unspecified",Unspecified intestinal parasitism,9
B83,9,B839,"Helminthiasis, unspecified","Helminthiasis, unspecified",Other helminthiases,9
B878,9,B8789,Myiasis of other sites,Myiasis of other sites,Myiasis of other sites,9
B88,9,B889,"Infestation, unspecified","Infestation, unspecified",Other infestations,9
B90,9,B909,Sequelae of respiratory and unspecified tuberculosis,Sequelae of respiratory and unspecified tuberculosis,Sequelae of tuberculosis,9
B94,9,B949,Sequelae of unspecified infectious and parasitic disease,Sequelae of unspecified infectious and parasitic disease,Sequelae of other and unspecified infectious and parasitic diseases,9
B962,9,B9629,Oth Escherichia coli as the cause of diseases classd elswhr,Other Escherichia coli [E. coli] as the cause of diseases classified elsewhere,Escherichia coli [E. coli ] as the cause of diseases classified elsewhere,9
B968,9,B9689,Oth bacterial agents as the cause of diseases classd elswhr,Other specified bacterial agents as the cause of diseases classified elsewhere,Other specified bacterial agents as the cause of diseases classified elsewhere,9
B971,9,B9719,Oth enterovirus as the cause of diseases classd elswhr,Other enterovirus as the cause of diseases classified elsewhere,Enterovirus as the cause of diseases classified elsewhere,9
B972,9,B9729,Oth coronavirus as the cause of diseases classd elswhr,Other coronavirus as the cause of diseases classified elsewhere,Coronavirus as the cause of diseases classified elsewhere,9
B973,9,B9739,Oth retrovirus as the cause of diseases classified elsewhere,Other retrovirus as the cause of diseases classified elsewhere,Retrovirus as the cause of diseases classified elsewhere,9
B978,9,B9789,Oth viral agents as the cause of diseases classd elswhr,Other viral agents as the cause of diseases classified elsewhere,Other viral agents as the cause of diseases classified elsewhere,9
B99,9,B999,Unspecified infectious disease,Unspecified infectious disease,Other and unspecified infectious diseases,9
C00,9,C009,"Malignant neoplasm of lip, unspecified","Malignant neoplasm of lip, unspecified",Malignant neoplasm of lip,9
C02,9,C029,"Malignant neoplasm of tongue, unspecified","Malignant neoplasm of tongue, unspecified",Malignant neoplasm of other and unspecified parts of tongue,9
C03,9,C039,"Malignant neoplasm of gum, unspecified","Malignant neoplasm of gum, unspecified",Malignant neoplasm of gum,9
C04,9,C049,"Malignant neoplasm of floor of mouth, unspecified","Malignant neoplasm of floor of mouth, unspecified",Malignant neoplasm of floor of mouth,9
C05,9,C059,"Malignant neoplasm of palate, unspecified","Malignant neoplasm of palate, unspecified",Malignant neoplasm of palate,9
C068,9,C0689,Malignant neoplasm of overlapping sites of oth prt mouth,Malignant neoplasm of overlapping sites of other parts of mouth,Malignant neoplasm of overlapping sites of other and unspecified parts of mouth,9
C08,9,C089,"Malignant neoplasm of major salivary gland, unspecified","Malignant neoplasm of major salivary gland, unspecified",Malignant neoplasm of other and unspecified major salivary glands,9
C09,9,C099,"Malignant neoplasm of tonsil, unspecified","Malignant neoplasm of tonsil, unspecified",Malignant neoplasm of tonsil,9
C10,9,C109,"Malignant neoplasm of oropharynx, unspecified","Malignant neoplasm of oropharynx, unspecified",Malignant neoplasm of oropharynx,9
C11,9,C119,"Malignant neoplasm of nasopharynx, unspecified","Malignant neoplasm of nasopharynx, unspecified",Malignant neoplasm of nasopharynx,9
C13,9,C139,"Malignant neoplasm of hypopharynx, unspecified","Malignant neoplasm of hypopharynx, unspecified",Malignant neoplasm of hypopharynx,9
C15,9,C159,"Malignant neoplasm of esophagus, unspecified","Malignant neoplasm of esophagus, unspecified",Malignant neoplasm of esophagus,9
C16,9,C169,"Malignant neoplasm of stomach, unspecified","Malignant neoplasm of stomach, unspecified",Malignant neoplasm of stomach,9
C17,9,C179,"Malignant neoplasm of small intestine, unspecified","Malignant neoplasm of small intestine, unspecified",Malignant neoplasm of small intestine,9
C18,9,C189,"Malignant neoplasm of colon, unspecified","Malignant neoplasm of colon, unspecified",Malignant neoplasm of colon,9
C22,9,C229,"Malig neoplasm of liver, not specified as primary or sec","Malignant neoplasm of liver, not specified as primary or secondary",Malignant neoplasm of liver and intrahepatic bile ducts,9
C24,9,C249,"Malignant neoplasm of biliary tract, unspecified","Malignant neoplasm of biliary tract, unspecified",Malignant neoplasm of other and unspecified parts of biliary tract,9
C25,9,C259,"Malignant neoplasm of pancreas, unspecified","Malignant neoplasm of pancreas, unspecified",Malignant neoplasm of pancreas,9
C26,9,C269,Malignant neoplasm of ill-defined sites within the dgstv sys,Malignant neoplasm of ill-defined sites within the digestive system,Malignant neoplasm of other and ill-defined digestive organs,9
C31,9,C319,"Malignant neoplasm of accessory sinus, unspecified","Malignant neoplasm of accessory sinus, unspecified",Malignant neoplasm of accessory sinuses,9
C32,9,C329,"Malignant neoplasm of larynx, unspecified","Malignant neoplasm of larynx, unspecified",Malignant neoplasm of larynx,9
C39,9,C399,"Malignant neoplasm of lower respiratory tract, part unsp","Malignant neoplasm of lower respiratory tract, part unspecified",Malignant neoplasm of other and ill-defined sites in the respiratory system and intrathoracic organs,9
C41,9,C419,"Malignant neoplasm of bone and articular cartilage, unsp","Malignant neoplasm of bone and articular cartilage, unspecified",Malignant neoplasm of bone and articular cartilage of other and unspecified sites,9
C433,9,C4339,Malignant melanoma of other parts of face,Malignant melanoma of other parts of face,Malignant melanoma of other and unspecified parts of face,9
C435,9,C4359,Malignant melanoma of other part of trunk,Malignant melanoma of other part of trunk,Malignant melanoma of trunk,9
C4A3,9,C4A39,Merkel cell carcinoma of other parts of face,Merkel cell carcinoma of other parts of face,Merkel cell carcinoma of other and unspecified parts of face,9
C4A5,9,C4A59,Merkel cell carcinoma of other part of trunk,Merkel cell carcinoma of other part of trunk,Merkel cell carcinoma of trunk,9
C440,9,C4409,Other specified malignant neoplasm of skin of lip,Other specified malignant neoplasm of skin of lip,Other and unspecified malignant neoplasm of skin of lip,9
C4410,9,C44109,"Unsp malignant neoplasm skin/ left eyelid, including canthus","Unspecified malignant neoplasm of skin of left eyelid, including canthus","Unspecified malignant neoplasm of skin of eyelid, including canthus",9
C4411,9,C44119,"Basal cell carcinoma skin/ left eyelid, including canthus","Basal cell carcinoma of skin of left eyelid, including canthus","Basal cell carcinoma of skin of eyelid, including canthus",9
C4412,9,C44129,"Squamous cell carcinoma skin/ left eyelid, including canthus","Squamous cell carcinoma of skin of left eyelid, including canthus","Squamous cell carcinoma of skin of eyelid, including canthus",9
C4419,9,C44199,"Oth malignant neoplasm skin/ left eyelid, including canthus","Other specified malignant neoplasm of skin of left eyelid, including canthus","Other specified malignant neoplasm of skin of eyelid, including canthus",9
C4420,9,C44209,Unsp malig neoplasm skin/ left ear and external auric canal,Unspecified malignant neoplasm of skin of left ear and external auricular canal,Unspecified malignant neoplasm of skin of ear and external auricular canal,9
C4421,9,C44219,Basal cell carcinoma skin/ left ear and external auric canal,Basal cell carcinoma of skin of left ear and external auricular canal,Basal cell carcinoma of skin of ear and external auricular canal,9
C4422,9,C44229,Squamous cell carcinoma skin/ left ear and extrn auric canal,Squamous cell carcinoma of skin of left ear and external auricular canal,Squamous cell carcinoma of skin of ear and external auricular canal,9
C4429,9,C44299,Oth malig neoplasm skin/ left ear and external auric canal,Other specified malignant neoplasm of skin of left ear and external auricular canal,Other specified malignant neoplasm of skin of ear and external auricular canal,9
C4430,9,C44309,Unsp malignant neoplasm of skin of other parts of face,Unspecified malignant neoplasm of skin of other parts of face,Unspecified malignant neoplasm of skin of other and unspecified parts of face,9
C4431,9,C44319,Basal cell carcinoma of skin of other parts of face,Basal cell carcinoma of skin of other parts of face,Basal cell carcinoma of skin of other and unspecified parts of face,9
C4432,9,C44329,Squamous cell carcinoma of skin of other parts of face,Squamous cell carcinoma of skin of other parts of face,Squamous cell carcinoma of skin of other and unspecified parts of face,9
C4439,9,C44399,Oth malignant neoplasm of skin of other parts of face,Other specified malignant neoplasm of skin of other parts of face,Other specified malignant neoplasm of skin of other and unspecified parts of face,9
C444,9,C4449,Other specified malignant neoplasm of skin of scalp and neck,Other specified malignant neoplasm of skin of scalp and neck,Other and unspecified malignant neoplasm of skin of scalp and neck,9
C4450,9,C44509,Unsp malignant neoplasm of skin of other part of trunk,Unspecified malignant neoplasm of skin of other part of trunk,Unspecified malignant neoplasm of skin of trunk,9
C4451,9,C44519,Basal cell carcinoma of skin of other part of trunk,Basal cell carcinoma of skin of other part of trunk,Basal cell carcinoma of skin of trunk,9
C4452,9,C44529,Squamous cell carcinoma of skin of other part of trunk,Squamous cell carcinoma of skin of other part of trunk,Squamous cell carcinoma of skin of trunk,9
C4459,9,C44599,Oth malignant neoplasm of skin of other part of trunk,Other specified malignant neoplasm of skin of other part of trunk,Other specified malignant neoplasm of skin of trunk,9
C4460,9,C44609,"Unsp malignant neoplasm skin/ left upper limb, inc shoulder","Unspecified malignant neoplasm of skin of left upper limb, including shoulder","Unspecified malignant neoplasm of skin of upper limb, including shoulder",9
C4461,9,C44619,"Basal cell carcinoma skin/ left upper limb, inc shoulder","Basal cell carcinoma of skin of left upper limb, including shoulder","Basal cell carcinoma of skin of upper limb, including shoulder",9
C4462,9,C44629,"Squamous cell carcinoma skin/ left upper limb, inc shoulder","Squamous cell carcinoma of skin of left upper limb, including shoulder","Squamous cell carcinoma of skin of upper limb, including shoulder",9
C4469,9,C44699,"Oth malignant neoplasm skin/ left upper limb, inc shoulder","Other specified malignant neoplasm of skin of left upper limb, including shoulder","Other specified malignant neoplasm of skin of upper limb, including shoulder",9
C4470,9,C44709,"Unsp malignant neoplasm skin/ left lower limb, including hip","Unspecified malignant neoplasm of skin of left lower limb, including hip","Unspecified malignant neoplasm of skin of lower limb, including hip",9
C4471,9,C44719,"Basal cell carcinoma skin/ left lower limb, including hip","Basal cell carcinoma of skin of left lower limb, including hip","Basal cell carcinoma of skin of lower limb, including hip",9
C4472,9,C44729,"Squamous cell carcinoma skin/ left lower limb, including hip","Squamous cell carcinoma of skin of left lower limb, including hip","Squamous cell carcinoma of skin of lower limb, including hip",9
C4479,9,C44799,"Oth malignant neoplasm skin/ left lower limb, including hip","Other specified malignant neoplasm of skin of left lower limb, including hip","Other specified malignant neoplasm of skin of lower limb, including hip",9
C448,9,C4489,Oth malignant neoplasm of overlapping sites of skin,Other specified malignant neoplasm of overlapping sites of skin,Other and unspecified malignant neoplasm of overlapping sites of skin,9
C449,9,C4499,"Other specified malignant neoplasm of skin, unspecified","Other specified malignant neoplasm of skin, unspecified","Other and unspecified malignant neoplasm of skin, unspecified",9
C45,9,C459,"Mesothelioma, unspecified","Mesothelioma, unspecified",Mesothelioma,9
C49A,9,C49A9,Gastrointestinal stromal tumor of other sites,Gastrointestinal stromal tumor of other sites,Gastrointestinal stromal tumor,9
C5001,9,C50019,"Malignant neoplasm of nipple and areola, unsp female breast","Malignant neoplasm of nipple and areola, unspecified female breast","Malignant neoplasm of nipple and areola, female",9
C5002,9,C50029,"Malignant neoplasm of nipple and areola, unsp male breast","Malignant neoplasm of nipple and areola, unspecified male breast","Malignant neoplasm of nipple and areola, male",9
C5011,9,C50119,Malignant neoplasm of central portion of unsp female breast,Malignant neoplasm of central portion of unspecified female breast,"Malignant neoplasm of central portion of breast, female",9
C5012,9,C50129,Malignant neoplasm of central portion of unsp male breast,Malignant neoplasm of central portion of unspecified male breast,"Malignant neoplasm of central portion of breast, male",9
C5021,9,C50219,Malig neoplasm of upper-inner quadrant of unsp female breast,Malignant neoplasm of upper-inner quadrant of unspecified female breast,"Malignant neoplasm of upper-inner quadrant of breast, female",9
C5022,9,C50229,Malig neoplasm of upper-inner quadrant of unsp male breast,Malignant neoplasm of upper-inner quadrant of unspecified male breast,"Malignant neoplasm of upper-inner quadrant of breast, male",9
C5031,9,C50319,Malig neoplasm of lower-inner quadrant of unsp female breast,Malignant neoplasm of lower-inner quadrant of unspecified female breast,"Malignant neoplasm of lower-inner quadrant of breast, female",9
C5032,9,C50329,Malig neoplasm of lower-inner quadrant of unsp male breast,Malignant neoplasm of lower-inner quadrant of unspecified male breast,"Malignant neoplasm of lower-inner quadrant of breast, male",9
C5041,9,C50419,Malig neoplasm of upper-outer quadrant of unsp female breast,Malignant neoplasm of upper-outer quadrant of unspecified female breast,"Malignant neoplasm of upper-outer quadrant of breast, female",9
C5042,9,C50429,Malig neoplasm of upper-outer quadrant of unsp male breast,Malignant neoplasm of upper-outer quadrant of unspecified male breast,"Malignant neoplasm of upper-outer quadrant of breast, male",9
C5051,9,C50519,Malig neoplasm of lower-outer quadrant of unsp female breast,Malignant neoplasm of lower-outer quadrant of unspecified female breast,"Malignant neoplasm of lower-outer quadrant of breast, female",9
C5052,9,C50529,Malig neoplasm of lower-outer quadrant of unsp male breast,Malignant neoplasm of lower-outer quadrant of unspecified male breast,"Malignant neoplasm of lower-outer quadrant of breast, male",9
C5061,9,C50619,Malignant neoplasm of axillary tail of unsp female breast,Malignant neoplasm of axillary tail of unspecified female breast,"Malignant neoplasm of axillary tail of breast, female",9
C5062,9,C50629,Malignant neoplasm of axillary tail of unsp male breast,Malignant neoplasm of axillary tail of unspecified male breast,"Malignant neoplasm of axillary tail of breast, male",9
C5081,9,C50819,Malignant neoplasm of ovrlp sites of unsp female breast,Malignant neoplasm of overlapping sites of unspecified female breast,"Malignant neoplasm of overlapping sites of breast, female",9
C5082,9,C50829,Malignant neoplasm of overlapping sites of unsp male breast,Malignant neoplasm of overlapping sites of unspecified male breast,"Malignant neoplasm of overlapping sites of breast, male",9
C5091,9,C50919,Malignant neoplasm of unsp site of unspecified female breast,Malignant neoplasm of unspecified site of unspecified female breast,"Malignant neoplasm of breast of unspecified site, female",9
C5092,9,C50929,Malignant neoplasm of unsp site of unspecified male breast,Malignant neoplasm of unspecified site of unspecified male breast,"Malignant neoplasm of breast of unspecified site, male",9
C51,9,C519,"Malignant neoplasm of vulva, unspecified","Malignant neoplasm of vulva, unspecified",Malignant neoplasm of vulva,9
C53,9,C539,"Malignant neoplasm of cervix uteri, unspecified","Malignant neoplasm of cervix uteri, unspecified",Malignant neoplasm of cervix uteri,9
C54,9,C549,"Malignant neoplasm of corpus uteri, unspecified","Malignant neoplasm of corpus uteri, unspecified",Malignant neoplasm of corpus uteri,9
C56,9,C569,Malignant neoplasm of unspecified ovary,Malignant neoplasm of unspecified ovary,Malignant neoplasm of ovary,9
C60,9,C609,"Malignant neoplasm of penis, unspecified","Malignant neoplasm of penis, unspecified",Malignant neoplasm of penis,9
C64,9,C649,"Malignant neoplasm of unsp kidney, except renal pelvis","Malignant neoplasm of unspecified kidney, except renal pelvis","Malignant neoplasm of kidney, except renal pelvis",9
C65,9,C659,Malignant neoplasm of unspecified renal pelvis,Malignant neoplasm of unspecified renal pelvis,Malignant neoplasm of renal pelvis,9
C66,9,C669,Malignant neoplasm of unspecified ureter,Malignant neoplasm of unspecified ureter,Malignant neoplasm of ureter,9
C67,9,C679,"Malignant neoplasm of bladder, unspecified","Malignant neoplasm of bladder, unspecified",Malignant neoplasm of bladder,9
C68,9,C689,"Malignant neoplasm of urinary organ, unspecified","Malignant neoplasm of urinary organ, unspecified",Malignant neoplasm of other and unspecified urinary organs,9
C70,9,C709,"Malignant neoplasm of meninges, unspecified","Malignant neoplasm of meninges, unspecified",Malignant neoplasm of meninges,9
C71,9,C719,"Malignant neoplasm of brain, unspecified","Malignant neoplasm of brain, unspecified",Malignant neoplasm of brain,9
C725,9,C7259,Malignant neoplasm of other cranial nerves,Malignant neoplasm of other cranial nerves,Malignant neoplasm of other and unspecified cranial nerves,9
C75,9,C759,"Malignant neoplasm of endocrine gland, unspecified","Malignant neoplasm of endocrine gland, unspecified",Malignant neoplasm of other endocrine glands and related structures,9
C7A01,9,C7A019,"Malignant carcinoid tumor of the sm int, unsp portion","Malignant carcinoid tumor of the small intestine, unspecified portion",Malignant carcinoid tumors of the small intestine,9
C7A02,9,C7A029,"Malignant carcinoid tumor of the lg int, unsp portion","Malignant carcinoid tumor of the large intestine, unspecified portion","Malignant carcinoid tumors of the appendix, large intestine, and rectum",9
C7B0,9,C7B09,Secondary carcinoid tumors of other sites,Secondary carcinoid tumors of other sites,Secondary carcinoid tumors,9
C77,9,C779,"Secondary and unsp malignant neoplasm of lymph node, unsp","Secondary and unspecified malignant neoplasm of lymph node, unspecified",Secondary and unspecified malignant neoplasm of lymph nodes,9
C783,9,C7839,Secondary malignant neoplasm of other respiratory organs,Secondary malignant neoplasm of other respiratory organs,Secondary malignant neoplasm of other and unspecified respiratory organs,9
C788,9,C7889,Secondary malignant neoplasm of other digestive organs,Secondary malignant neoplasm of other digestive organs,Secondary malignant neoplasm of other and unspecified digestive organs,9
C791,9,C7919,Secondary malignant neoplasm of other urinary organs,Secondary malignant neoplasm of other urinary organs,Secondary malignant neoplasm of bladder and other and unspecified urinary organs,9
C794,9,C7949,Secondary malignant neoplasm of oth parts of nervous system,Secondary malignant neoplasm of other parts of nervous system,Secondary malignant neoplasm of other and unspecified parts of nervous system,9
C798,9,C7989,Secondary malignant neoplasm of other specified sites,Secondary malignant neoplasm of other specified sites,Secondary malignant neoplasm of other specified sites,9
C810,9,C8109,"Nodlr lymphocy predom Hdgkn lymph, extrnod & solid org site","Nodular lymphocyte predominant Hodgkin lymphoma, extranodal and solid organ sites",Nodular lymphocyte predominant Hodgkin lymphoma,9
C811,9,C8119,"Nodular scler Hodgkin lymph, extrnod and solid organ sites","Nodular sclerosis Hodgkin lymphoma, extranodal and solid organ sites",Nodular sclerosis Hodgkin lymphoma,9
C812,9,C8129,"Mixed cellular Hodgkin lymph, extrnod and solid organ sites","Mixed cellularity Hodgkin lymphoma, extranodal and solid organ sites",Mixed cellularity Hodgkin lymphoma,9
C813,9,C8139,"Lymphocy deplet Hodgkin lymph, extrnod and solid organ sites","Lymphocyte depleted Hodgkin lymphoma, extranodal and solid organ sites",Lymphocyte depleted Hodgkin lymphoma,9
C814,9,C8149,"Lymp-rich Hodgkin lymphoma, extranodal and solid organ sites","Lymphocyte-rich Hodgkin lymphoma, extranodal and solid organ sites",Lymphocyte-rich Hodgkin lymphoma,9
C817,9,C8179,"Other Hodgkin lymphoma, extranodal and solid organ sites","Other Hodgkin lymphoma, extranodal and solid organ sites",Other Hodgkin lymphoma,9
C819,9,C8199,"Hodgkin lymphoma, unsp, extranodal and solid organ sites","Hodgkin lymphoma, unspecified, extranodal and solid organ sites","Hodgkin lymphoma, unspecified",9
C820,9,C8209,"Follicular lymphoma grade I, extrnod and solid organ sites","Follicular lymphoma grade I, extranodal and solid organ sites",Follicular lymphoma grade I,9
C821,9,C8219,"Follicular lymphoma grade II, extrnod and solid organ sites","Follicular lymphoma grade II, extranodal and solid organ sites",Follicular lymphoma grade II,9
C822,9,C8229,"Foliclar lymph grade III, unsp, extrnod and solid org sites","Follicular lymphoma grade III, unspecified, extranodal and solid organ sites","Follicular lymphoma grade III, unspecified",9
C823,9,C8239,"Foliclar lymphoma grade IIIa, extrnod and solid organ sites","Follicular lymphoma grade IIIa, extranodal and solid organ sites",Follicular lymphoma grade IIIa,9
C824,9,C8249,"Foliclar lymphoma grade IIIb, extrnod and solid organ sites","Follicular lymphoma grade IIIb, extranodal and solid organ sites",Follicular lymphoma grade IIIb,9
C825,9,C8259,"Diffuse folicl center lymph, extrnod and solid organ sites","Diffuse follicle center lymphoma, extranodal and solid organ sites",Diffuse follicle center lymphoma,9
C826,9,C8269,"Cutan folicl center lymphoma, extrnod and solid organ sites","Cutaneous follicle center lymphoma, extranodal and solid organ sites",Cutaneous follicle center lymphoma,9
C828,9,C8289,"Oth types of foliclar lymph, extrnod and solid organ sites","Other types of follicular lymphoma, extranodal and solid organ sites",Other types of follicular lymphoma,9
C829,9,C8299,"Follicular lymphoma, unsp, extranodal and solid organ sites","Follicular lymphoma, unspecified, extranodal and solid organ sites","Follicular lymphoma, unspecified",9
C830,9,C8309,"Small cell B-cell lymphoma, extranodal and solid organ sites","Small cell B-cell lymphoma, extranodal and solid organ sites",Small cell B-cell lymphoma,9
C831,9,C8319,"Mantle cell lymphoma, extranodal and solid organ sites","Mantle cell lymphoma, extranodal and solid organ sites",Mantle cell lymphoma,9
C833,9,C8339,"Diffuse large B-cell lymphoma, extrnod and solid organ sites","Diffuse large B-cell lymphoma, extranodal and solid organ sites",Diffuse large B-cell lymphoma,9
C835,9,C8359,"Lymphoblastic lymphoma, extrnod and solid organ sites","Lymphoblastic (diffuse) lymphoma, extranodal and solid organ sites",Lymphoblastic (diffuse) lymphoma,9
C837,9,C8379,"Burkitt lymphoma, extranodal and solid organ sites","Burkitt lymphoma, extranodal and solid organ sites",Burkitt lymphoma,9
C838,9,C8389,"Oth non-follic lymphoma, extranodal and solid organ sites","Other non-follicular lymphoma, extranodal and solid organ sites",Other non-follicular lymphoma,9
C839,9,C8399,"Non-follic lymphoma, unsp, extrnod and solid organ sites","Non-follicular (diffuse) lymphoma, unspecified, extranodal and solid organ sites","Non-follicular (diffuse) lymphoma, unspecified",9
C840,9,C8409,"Mycosis fungoides, extranodal and solid organ sites","Mycosis fungoides, extranodal and solid organ sites",Mycosis fungoides,9
C841,9,C8419,"Sezary disease, extranodal and solid organ sites","Sezary disease, extranodal and solid organ sites",Sezary disease,9
C844,9,C8449,"Prph T-cell lymph, not class, extrnod and solid organ sites","Peripheral T-cell lymphoma, not classified, extranodal and solid organ sites","Peripheral T-cell lymphoma, not classified",9
C846,9,C8469,"Anaplstc lg cell lymph, ALK-pos, extrnod and solid org sites","Anaplastic large cell lymphoma, ALK-positive, extranodal and solid organ sites","Anaplastic large cell lymphoma, ALK-positive",9
C847,9,C8479,"Anaplstc lg cell lymph, ALK-neg, extrnod and solid org sites","Anaplastic large cell lymphoma, ALK-negative, extranodal and solid organ sites","Anaplastic large cell lymphoma, ALK-negative",9
C84A,9,C84A9,"Cutan T-cell lymphoma, unsp, extrnod and solid organ sites","Cutaneous T-cell lymphoma, unspecified, extranodal and solid organ sites","Cutaneous T-cell lymphoma, unspecified",9
C84Z,9,C84Z9,"Oth mature T/NK-cell lymph, extrnod and solid organ sites","Other mature T/NK-cell lymphomas, extranodal and solid organ sites",Other mature T/NK-cell lymphomas,9
C849,9,C8499,"Mature T/NK-cell lymph, unsp, extrnod and solid organ sites","Mature T/NK-cell lymphomas, unspecified, extranodal and solid organ sites","Mature T/NK-cell lymphomas, unspecified",9
C851,9,C8519,"Unsp B-cell lymphoma, extranodal and solid organ sites","Unspecified B-cell lymphoma, extranodal and solid organ sites",Unspecified B-cell lymphoma,9
C852,9,C8529,"Mediastnl large B-cell lymph, extrnod and solid organ sites","Mediastinal (thymic) large B-cell lymphoma, extranodal and solid organ sites",Mediastinal (thymic) large B-cell lymphoma,9
C858,9,C8589,"Oth types of non-hodg lymph, extrnod and solid organ sites","Other specified types of non-Hodgkin lymphoma, extranodal and solid organ sites",Other specified types of non-Hodgkin lymphoma,9
C859,9,C8599,"Non-Hodgkin lymphoma, unsp, extranodal and solid organ sites","Non-Hodgkin lymphoma, unspecified, extranodal and solid organ sites","Non-Hodgkin lymphoma, unspecified",9
C88,9,C889,"Malignant immunoproliferative disease, unspecified","Malignant immunoproliferative disease, unspecified",Malignant immunoproliferative diseases and certain other B-cell lymphomas,9
C962,9,C9629,Other malignant mast cell neoplasm,Other malignant mast cell neoplasm,Malignant mast cell neoplasm,9
D014,9,D0149,Carcinoma in situ of other parts of intestine,Carcinoma in situ of other parts of intestine,Carcinoma in situ of other and unspecified parts of intestine,9
D033,9,D0339,Melanoma in situ of other parts of face,Melanoma in situ of other parts of face,Melanoma in situ of other and unspecified parts of face,9
D035,9,D0359,Melanoma in situ of other part of trunk,Melanoma in situ of other part of trunk,Melanoma in situ of trunk,9
D043,9,D0439,Carcinoma in situ of skin of other parts of face,Carcinoma in situ of skin of other parts of face,Carcinoma in situ of skin of other and unspecified parts of face,9
D06,9,D069,"Carcinoma in situ of cervix, unspecified","Carcinoma in situ of cervix, unspecified",Carcinoma in situ of cervix uteri,9
D073,9,D0739,Carcinoma in situ of other female genital organs,Carcinoma in situ of other female genital organs,Carcinoma in situ of other and unspecified female genital organs,9
D076,9,D0769,Carcinoma in situ of other male genital organs,Carcinoma in situ of other male genital organs,Carcinoma in situ of other and unspecified male genital organs,9
D091,9,D0919,Carcinoma in situ of other urinary organs,Carcinoma in situ of other urinary organs,Carcinoma in situ of other and unspecified urinary organs,9
D103,9,D1039,Benign neoplasm of other parts of mouth,Benign neoplasm of other parts of mouth,Benign neoplasm of other and unspecified parts of mouth,9
D11,9,D119,"Benign neoplasm of major salivary gland, unspecified","Benign neoplasm of major salivary gland, unspecified",Benign neoplasm of major salivary glands,9
D12,9,D129,Benign neoplasm of anus and anal canal,Benign neoplasm of anus and anal canal,"Benign neoplasm of colon, rectum, anus and anal canal",9
D133,9,D1339,Benign neoplasm of other parts of small intestine,Benign neoplasm of other parts of small intestine,Benign neoplasm of other and unspecified parts of small intestine,9
D15,9,D159,"Benign neoplasm of intrathoracic organ, unspecified","Benign neoplasm of intrathoracic organ, unspecified",Benign neoplasm of other and unspecified intrathoracic organs,9
D173,9,D1739,"Benign lipomatous neoplasm of skin, subcu of sites",Benign lipomatous neoplasm of skin and subcutaneous tissue of other sites,Benign lipomatous neoplasm of skin and subcutaneous tissue of other and unspecified sites,9
D177,9,D1779,Benign lipomatous neoplasm of other sites,Benign lipomatous neoplasm of other sites,Benign lipomatous neoplasm of other sites,9
D180,9,D1809,Hemangioma of other sites,Hemangioma of other sites,Hemangioma,9
D19,9,D199,"Benign neoplasm of mesothelial tissue, unspecified","Benign neoplasm of mesothelial tissue, unspecified",Benign neoplasm of mesothelial tissue,9
D223,9,D2239,Melanocytic nevi of other parts of face,Melanocytic nevi of other parts of face,Melanocytic nevi of other and unspecified parts of face,9
D233,9,D2339,Other benign neoplasm of skin of other parts of face,Other benign neoplasm of skin of other parts of face,Other benign neoplasm of skin of other and unspecified parts of face,9
D24,9,D249,Benign neoplasm of unspecified breast,Benign neoplasm of unspecified breast,Benign neoplasm of breast,9
D25,9,D259,"Leiomyoma of uterus, unspecified","Leiomyoma of uterus, unspecified",Leiomyoma of uterus,9
D26,9,D269,"Other benign neoplasm of uterus, unspecified","Other benign neoplasm of uterus, unspecified",Other benign neoplasms of uterus,9
D27,9,D279,Benign neoplasm of unspecified ovary,Benign neoplasm of unspecified ovary,Benign neoplasm of ovary,9
D28,9,D289,"Benign neoplasm of female genital organ, unspecified","Benign neoplasm of female genital organ, unspecified",Benign neoplasm of other and unspecified female genital organs,9
D32,9,D329,"Benign neoplasm of meninges, unspecified","Benign neoplasm of meninges, unspecified",Benign neoplasm of meninges,9
D33,9,D339,"Benign neoplasm of central nervous system, unspecified","Benign neoplasm of central nervous system, unspecified",Benign neoplasm of brain and other parts of central nervous system,9
D3A01,9,D3A019,"Benign carcinoid tumor of the small intestine, unsp portion","Benign carcinoid tumor of the small intestine, unspecified portion",Benign carcinoid tumors of the small intestine,9
D3A02,9,D3A029,"Benign carcinoid tumor of the large intestine, unsp portion","Benign carcinoid tumor of the large intestine, unspecified portion","Benign carcinoid tumors of the appendix, large intestine, and rectum",9
D3703,9,D37039,"Neoplasm of uncrt behavior of the major salivary gland, unsp","Neoplasm of uncertain behavior of the major salivary glands, unspecified",Neoplasm of uncertain behavior of the major salivary glands,9
D42,9,D429,"Neoplasm of uncertain behavior of meninges, unspecified","Neoplasm of uncertain behavior of meninges, unspecified",Neoplasm of uncertain behavior of meninges,9
D43,9,D439,"Neoplasm of uncertain behavior of cnsl, unsp","Neoplasm of uncertain behavior of central nervous system, unspecified",Neoplasm of uncertain behavior of brain and central nervous system,9
E751,9,E7519,Other gangliosidosis,Other gangliosidosis,Other and unspecified gangliosidosis,9
D470,9,D4709,Other mast cell neoplasms of uncertain behavior,Other mast cell neoplasms of uncertain behavior,Mast cell neoplasms of uncertain behavior,9
D47Z,9,D47Z9,"Oth neoplm of uncrt behav of lymphoid, hematpoetc & rel tiss","Other specified neoplasms of uncertain behavior of lymphoid, hematopoietic and related tissue","Other specified neoplasms of uncertain behavior of lymphoid, hematopoietic and related tissue",9
D4951,9,D49519,Neoplasm of unspecified behavior of unspecified kidney,Neoplasm of unspecified behavior of unspecified kidney,Neoplasm of unspecified behavior of kidney,9
D498,9,D4989,Neoplasm of unspecified behavior of other specified sites,Neoplasm of unspecified behavior of other specified sites,Neoplasm of unspecified behavior of other specified sites,9
D50,9,D509,"Iron deficiency anemia, unspecified","Iron deficiency anemia, unspecified",Iron deficiency anemia,9
D51,9,D519,"Vitamin B12 deficiency anemia, unspecified","Vitamin B12 deficiency anemia, unspecified",Vitamin B12 deficiency anemia,9
D52,9,D529,"Folate deficiency anemia, unspecified","Folate deficiency anemia, unspecified",Folate deficiency anemia,9
D53,9,D539,"Nutritional anemia, unspecified","Nutritional anemia, unspecified",Other nutritional anemias,9
D55,9,D559,"Anemia due to enzyme disorder, unspecified","Anemia due to enzyme disorder, unspecified",Anemia due to enzyme disorders,9
D56,9,D569,"Thalassemia, unspecified","Thalassemia, unspecified",Thalassemia,9
D5721,9,D57219,"Sickle-cell/Hb-C disease with crisis, unspecified","Sickle-cell/Hb-C disease with crisis, unspecified",Sickle-cell/Hb-C disease with crisis,9
D5741,9,D57419,"Sickle-cell thalassemia with crisis, unspecified","Sickle-cell thalassemia with crisis, unspecified",Sickle-cell thalassemia with crisis,9
D5781,9,D57819,"Other sickle-cell disorders with crisis, unspecified","Other sickle-cell disorders with crisis, unspecified",Other sickle-cell disorders with crisis,9
D58,9,D589,"Hereditary hemolytic anemia, unspecified","Hereditary hemolytic anemia, unspecified",Other hereditary hemolytic anemias,9
D59,9,D599,"Acquired hemolytic anemia, unspecified","Acquired hemolytic anemia, unspecified",Acquired hemolytic anemia,9
D60,9,D609,"Acquired pure red cell aplasia, unspecified","Acquired pure red cell aplasia, unspecified",Acquired pure red cell aplasia [erythroblastopenia],9
D610,9,D6109,Other constitutional aplastic anemia,Other constitutional aplastic anemia,Constitutional aplastic anemia,9
D648,9,D6489,Other specified anemias,Other specified anemias,Other specified anemias,9
D685,9,D6859,Other primary thrombophilia,Other primary thrombophilia,Primary thrombophilia,9
D686,9,D6869,Other thrombophilia,Other thrombophilia,Other thrombophilia,9
D694,9,D6949,Other primary thrombocytopenia,Other primary thrombocytopenia,Other primary thrombocytopenia,9
D695,9,D6959,Other secondary thrombocytopenia,Other secondary thrombocytopenia,Secondary thrombocytopenia,9
D70,9,D709,"Neutropenia, unspecified","Neutropenia, unspecified",Neutropenia,9
D7281,9,D72819,"Decreased white blood cell count, unspecified","Decreased white blood cell count, unspecified",Decreased white blood cell count,9
D7282,9,D72829,"Elevated white blood cell count, unspecified","Elevated white blood cell count, unspecified",Elevated white blood cell count,9
D738,9,D7389,Other diseases of spleen,Other diseases of spleen,Other diseases of spleen,9
D74,9,D749,"Methemoglobinemia, unspecified","Methemoglobinemia, unspecified",Methemoglobinemia,9
D758,9,D7589,Other specified diseases of blood and blood-forming organs,Other specified diseases of blood and blood-forming organs,Other specified diseases of blood and blood-forming organs,9
D788,9,D7889,Other postprocedural complications of the spleen,Other postprocedural complications of the spleen,Other intraoperative and postprocedural complications of the spleen,9
D80,9,D809,"Immunodeficiency with predominantly antibody defects, unsp","Immunodeficiency with predominantly antibody defects, unspecified",Immunodeficiency with predominantly antibody defects,9
D8181,9,D81819,"Biotin-dependent carboxylase deficiency, unspecified","Biotin-dependent carboxylase deficiency, unspecified",Biotin-dependent carboxylase deficiency,9
D82,9,D829,"Immunodeficiency associated with major defect, unspecified","Immunodeficiency associated with major defect, unspecified",Immunodeficiency associated with other major defects,9
D83,9,D839,"Common variable immunodeficiency, unspecified","Common variable immunodeficiency, unspecified",Common variable immunodeficiency,9
D84,9,D849,"Immunodeficiency, unspecified","Immunodeficiency, unspecified",Other immunodeficiencies,9
D868,9,D8689,Sarcoidosis of other sites,Sarcoidosis of other sites,Sarcoidosis of other sites,9
D894,9,D8949,Other mast cell activation disorder,Other mast cell activation disorder,Mast cell activation syndrome and related disorders,9
E00,9,E009,"Congenital iodine-deficiency syndrome, unspecified","Congenital iodine-deficiency syndrome, unspecified",Congenital iodine-deficiency syndrome,9
E03,9,E039,"Hypothyroidism, unspecified","Hypothyroidism, unspecified",Other hypothyroidism,9
E04,9,E049,"Nontoxic goiter, unspecified","Nontoxic goiter, unspecified",Other nontoxic goiter,9
E06,9,E069,"Thyroiditis, unspecified","Thyroiditis, unspecified",Thyroiditis,9
E078,9,E0789,Other specified disorders of thyroid,Other specified disorders of thyroid,Other specified disorders of thyroid,9
E082,9,E0829,Diabetes due to undrl condition w oth diabetic kidney comp,Diabetes mellitus due to underlying condition with other diabetic kidney complication,Diabetes mellitus due to underlying condition with kidney complications,9
E0831,9,E08319,Diab due to undrl cond w unsp diab rtnop w/o macular edema,Diabetes mellitus due to underlying condition with unspecified diabetic retinopathy without macular edema,Diabetes mellitus due to underlying condition with unspecified diabetic retinopathy,9
E08321,9,E083219,"Diabetes with mild nonp rtnop with macular edema, unsp","Diabetes mellitus due to underlying condition with mild nonproliferative diabetic retinopathy with macular edema, unspecified eye",Diabetes mellitus due to underlying condition with mild nonproliferative diabetic retinopathy with macular edema,9
E112,9,E1129,Type 2 diabetes mellitus w oth diabetic kidney complication,Type 2 diabetes mellitus with other diabetic kidney complication,Type 2 diabetes mellitus with kidney complications,9
A369,0,A369,"Diphtheria, unspecified","Diphtheria, unspecified","Diphtheria, unspecified",9
E08329,9,E083299,"Diabetes with mild nonp rtnop without macular edema, unsp","Diabetes mellitus due to underlying condition with mild nonproliferative diabetic retinopathy without macular edema, unspecified eye",Diabetes mellitus due to underlying condition with mild nonproliferative diabetic retinopathy without macular edema,9
E08331,9,E083319,"Diabetes with moderate nonp rtnop with macular edema, unsp","Diabetes mellitus due to underlying condition with moderate nonproliferative diabetic retinopathy with macular edema, unspecified eye",Diabetes mellitus due to underlying condition with moderate nonproliferative diabetic retinopathy with macular edema,9
E08339,9,E083399,"Diab with moderate nonp rtnop without macular edema, unsp","Diabetes mellitus due to underlying condition with moderate nonproliferative diabetic retinopathy without macular edema, unspecified eye",Diabetes mellitus due to underlying condition with moderate nonproliferative diabetic retinopathy without macular edema,9
E08341,9,E083419,"Diabetes with severe nonp rtnop with macular edema, unsp","Diabetes mellitus due to underlying condition with severe nonproliferative diabetic retinopathy with macular edema, unspecified eye",Diabetes mellitus due to underlying condition with severe nonproliferative diabetic retinopathy with macular edema,9
E08349,9,E083499,"Diabetes with severe nonp rtnop without macular edema, unsp","Diabetes mellitus due to underlying condition with severe nonproliferative diabetic retinopathy without macular edema, unspecified eye",Diabetes mellitus due to underlying condition with severe nonproliferative diabetic retinopathy without macular edema,9
E08351,9,E083519,"Diabetes with prolif diabetic rtnop with macular edema, unsp","Diabetes mellitus due to underlying condition with proliferative diabetic retinopathy with macular edema, unspecified eye",Diabetes mellitus due to underlying condition with proliferative diabetic retinopathy with macular edema,9
E08352,9,E083529,"Diab with prolif diabetic rtnop with trctn dtch macula, unsp","Diabetes mellitus due to underlying condition with proliferative diabetic retinopathy with traction retinal detachment involving the macula, unspecified eye",Diabetes mellitus due to underlying condition with proliferative diabetic retinopathy with traction retinal detachment involving the macula,9
E08353,9,E083539,"Diab with prolif diabetic rtnop with trctn dtch n-mcla, unsp","Diabetes mellitus due to underlying condition with proliferative diabetic retinopathy with traction retinal detachment not involving the macula, unspecified eye",Diabetes mellitus due to underlying condition with proliferative diabetic retinopathy with traction retinal detachment not involving the macula,9
E08354,9,E083549,"Diabetes with prolif diabetic rtnop with comb detach, unsp","Diabetes mellitus due to underlying condition with proliferative diabetic retinopathy with combined traction retinal detachment and rhegmatogenous retinal detachment, unspecified eye",Diabetes mellitus due to underlying condition with proliferative diabetic retinopathy with combined traction retinal detachment and rhegmatogenous retinal detachment,9
E08355,9,E083559,"Diabetes with stable prolif diabetic retinopathy, unsp","Diabetes mellitus due to underlying condition with stable proliferative diabetic retinopathy, unspecified eye",Diabetes mellitus due to underlying condition with stable proliferative diabetic retinopathy,9
E08359,9,E083599,"Diab with prolif diabetic rtnop without macular edema, unsp","Diabetes mellitus due to underlying condition with proliferative diabetic retinopathy without macular edema, unspecified eye",Diabetes mellitus due to underlying condition with proliferative diabetic retinopathy without macular edema,9
E084,9,E0849,Diabetes due to undrl condition w oth diabetic neuro comp,Diabetes mellitus due to underlying condition with other diabetic neurological complication,Diabetes mellitus due to underlying condition with neurological complications,9
E085,9,E0859,Diabetes due to underlying condition w oth circulatory comp,Diabetes mellitus due to underlying condition with other circulatory complications,Diabetes mellitus due to underlying condition with circulatory complications,9
E0864,9,E08649,Diabetes due to underlying condition w hypoglycemia w/o coma,Diabetes mellitus due to underlying condition with hypoglycemia without coma,Diabetes mellitus due to underlying condition with hypoglycemia,9
E092,9,E0929,Drug/chem diabetes w oth diabetic kidney complication,Drug or chemical induced diabetes mellitus with other diabetic kidney complication,Drug or chemical induced diabetes mellitus with kidney complications,9
E0931,9,E09319,Drug/chem diabetes w unsp diabetic rtnop w/o macular edema,Drug or chemical induced diabetes mellitus with unspecified diabetic retinopathy without macular edema,Drug or chemical induced diabetes mellitus with unspecified diabetic retinopathy,9
E09321,9,E093219,"Drug/chem diab with mild nonp rtnop with macular edema, unsp","Drug or chemical induced diabetes mellitus with mild nonproliferative diabetic retinopathy with macular edema, unspecified eye",Drug or chemical induced diabetes mellitus with mild nonproliferative diabetic retinopathy with macular edema,9
E09329,9,E093299,"Drug/chem diab with mild nonp rtnop without mclr edema, unsp","Drug or chemical induced diabetes mellitus with mild nonproliferative diabetic retinopathy without macular edema, unspecified eye",Drug or chemical induced diabetes mellitus with mild nonproliferative diabetic retinopathy without macular edema,9
E09331,9,E093319,"Drug/chem diab with mod nonp rtnop with macular edema, unsp","Drug or chemical induced diabetes mellitus with moderate nonproliferative diabetic retinopathy with macular edema, unspecified eye",Drug or chemical induced diabetes mellitus with moderate nonproliferative diabetic retinopathy with macular edema,9
E09339,9,E093399,"Drug/chem diab with mod nonp rtnop without mclr edema, unsp","Drug or chemical induced diabetes mellitus with moderate nonproliferative diabetic retinopathy without macular edema, unspecified eye",Drug or chemical induced diabetes mellitus with moderate nonproliferative diabetic retinopathy without macular edema,9
E09341,9,E093419,"Drug/chem diab with severe nonp rtnop with mclr edema, unsp","Drug or chemical induced diabetes mellitus with severe nonproliferative diabetic retinopathy with macular edema, unspecified eye",Drug or chemical induced diabetes mellitus with severe nonproliferative diabetic retinopathy with macular edema,9
E09349,9,E093499,"Drug/chem diab with severe nonp rtnop w/o mclr edema, unsp","Drug or chemical induced diabetes mellitus with severe nonproliferative diabetic retinopathy without macular edema, unspecified eye",Drug or chemical induced diabetes mellitus with severe nonproliferative diabetic retinopathy without macular edema,9
E09351,9,E093519,"Drug/chem diab with prolif diab rtnop with mclr edema, unsp","Drug or chemical induced diabetes mellitus with proliferative diabetic retinopathy with macular edema, unspecified eye",Drug or chemical induced diabetes mellitus with proliferative diabetic retinopathy with macular edema,9
E09352,9,E093529,"Drug/chem diab w prolif diab rtnop w trctn dtch macula, unsp","Drug or chemical induced diabetes mellitus with proliferative diabetic retinopathy with traction retinal detachment involving the macula, unspecified eye",Drug or chemical induced diabetes mellitus with proliferative diabetic retinopathy with traction retinal detachment involving the macula,9
E09353,9,E093539,"Drug/chem diab w prolif diab rtnop w trctn dtch n-mcla, unsp","Drug or chemical induced diabetes mellitus with proliferative diabetic retinopathy with traction retinal detachment not involving the macula, unspecified eye",Drug or chemical induced diabetes mellitus with proliferative diabetic retinopathy with traction retinal detachment not involving the macula,9
E09354,9,E093549,"Drug/chem diab with prolif diab rtnop with comb detach, unsp","Drug or chemical induced diabetes mellitus with proliferative diabetic retinopathy with combined traction retinal detachment and rhegmatogenous retinal detachment, unspecified eye",Drug or chemical induced diabetes mellitus with proliferative diabetic retinopathy with combined traction retinal detachment and rhegmatogenous retinal detachment,9
E09355,9,E093559,"Drug/chem diabetes with stable prolif diabetic rtnop, unsp","Drug or chemical induced diabetes mellitus with stable proliferative diabetic retinopathy, unspecified eye",Drug or chemical induced diabetes mellitus with stable proliferative diabetic retinopathy,9
E09359,9,E093599,"Drug/chem diab with prolif diab rtnop w/o mclr edema, unsp","Drug or chemical induced diabetes mellitus with proliferative diabetic retinopathy without macular edema, unspecified eye",Drug or chemical induced diabetes mellitus with proliferative diabetic retinopathy without macular edema,9
E094,9,E0949,Drug/chem diabetes w neuro comp w oth diabetic neuro comp,Drug or chemical induced diabetes mellitus with neurological complications with other diabetic neurological complication,Drug or chemical induced diabetes mellitus with neurological complications,9
E095,9,E0959,Drug/chem diabetes mellitus w oth circulatory complications,Drug or chemical induced diabetes mellitus with other circulatory complications,Drug or chemical induced diabetes mellitus with circulatory complications,9
E0964,9,E09649,Drug/chem diabetes mellitus w hypoglycemia w/o coma,Drug or chemical induced diabetes mellitus with hypoglycemia without coma,Drug or chemical induced diabetes mellitus with hypoglycemia,9
E102,9,E1029,Type 1 diabetes mellitus w oth diabetic kidney complication,Type 1 diabetes mellitus with other diabetic kidney complication,Type 1 diabetes mellitus with kidney complications,9
E1031,9,E10319,Type 1 diabetes w unsp diabetic rtnop w/o macular edema,Type 1 diabetes mellitus with unspecified diabetic retinopathy without macular edema,Type 1 diabetes mellitus with unspecified diabetic retinopathy,9
E10321,9,E103219,"Type 1 diab with mild nonp rtnop with macular edema, unsp","Type 1 diabetes mellitus with mild nonproliferative diabetic retinopathy with macular edema, unspecified eye",Type 1 diabetes mellitus with mild nonproliferative diabetic retinopathy with macular edema,9
E10329,9,E103299,"Type 1 diab with mild nonp rtnop without macular edema, unsp","Type 1 diabetes mellitus with mild nonproliferative diabetic retinopathy without macular edema, unspecified eye",Type 1 diabetes mellitus with mild nonproliferative diabetic retinopathy without macular edema,9
E10331,9,E103319,"Type 1 diab with mod nonp rtnop with macular edema, unsp","Type 1 diabetes mellitus with moderate nonproliferative diabetic retinopathy with macular edema, unspecified eye",Type 1 diabetes mellitus with moderate nonproliferative diabetic retinopathy with macular edema,9
E10339,9,E103399,"Type 1 diab with mod nonp rtnop without macular edema, unsp","Type 1 diabetes mellitus with moderate nonproliferative diabetic retinopathy without macular edema, unspecified eye",Type 1 diabetes mellitus with moderate nonproliferative diabetic retinopathy without macular edema,9
E10341,9,E103419,"Type 1 diab with severe nonp rtnop with macular edema, unsp","Type 1 diabetes mellitus with severe nonproliferative diabetic retinopathy with macular edema, unspecified eye",Type 1 diabetes mellitus with severe nonproliferative diabetic retinopathy with macular edema,9
E10349,9,E103499,"Type 1 diab with severe nonp rtnop without mclr edema, unsp","Type 1 diabetes mellitus with severe nonproliferative diabetic retinopathy without macular edema, unspecified eye",Type 1 diabetes mellitus with severe nonproliferative diabetic retinopathy without macular edema,9
E10351,9,E103519,"Type 1 diab with prolif diab rtnop with macular edema, unsp","Type 1 diabetes mellitus with proliferative diabetic retinopathy with macular edema, unspecified eye",Type 1 diabetes mellitus with proliferative diabetic retinopathy with macular edema,9
E10352,9,E103529,"Type 1 diab w prolif diab rtnop with trctn dtch macula, unsp","Type 1 diabetes mellitus with proliferative diabetic retinopathy with traction retinal detachment involving the macula, unspecified eye",Type 1 diabetes mellitus with proliferative diabetic retinopathy with traction retinal detachment involving the macula,9
E10353,9,E103539,"Type 1 diab w prolif diab rtnop with trctn dtch n-mcla, unsp","Type 1 diabetes mellitus with proliferative diabetic retinopathy with traction retinal detachment not involving the macula, unspecified eye",Type 1 diabetes mellitus with proliferative diabetic retinopathy with traction retinal detachment not involving the macula,9
E10354,9,E103549,"Type 1 diab with prolif diab rtnop with comb detach, unsp","Type 1 diabetes mellitus with proliferative diabetic retinopathy with combined traction retinal detachment and rhegmatogenous retinal detachment, unspecified eye",Type 1 diabetes mellitus with proliferative diabetic retinopathy with combined traction retinal detachment and rhegmatogenous retinal detachment,9
E10355,9,E103559,"Type 1 diabetes with stable prolif diabetic rtnop, unsp","Type 1 diabetes mellitus with stable proliferative diabetic retinopathy, unspecified eye",Type 1 diabetes mellitus with stable proliferative diabetic retinopathy,9
E10359,9,E103599,"Type 1 diab with prolif diab rtnop without mclr edema, unsp","Type 1 diabetes mellitus with proliferative diabetic retinopathy without macular edema, unspecified eye",Type 1 diabetes mellitus with proliferative diabetic retinopathy without macular edema,9
E104,9,E1049,Type 1 diabetes w oth diabetic neurological complication,Type 1 diabetes mellitus with other diabetic neurological complication,Type 1 diabetes mellitus with neurological complications,9
E105,9,E1059,Type 1 diabetes mellitus with oth circulatory complications,Type 1 diabetes mellitus with other circulatory complications,Type 1 diabetes mellitus with circulatory complications,9
E1064,9,E10649,Type 1 diabetes mellitus with hypoglycemia without coma,Type 1 diabetes mellitus with hypoglycemia without coma,Type 1 diabetes mellitus with hypoglycemia,9
E7524,9,E75249,"Niemann-Pick disease, unspecified","Niemann-Pick disease, unspecified",Niemann-Pick disease,9
E1131,9,E11319,Type 2 diabetes w unsp diabetic rtnop w/o macular edema,Type 2 diabetes mellitus with unspecified diabetic retinopathy without macular edema,Type 2 diabetes mellitus with unspecified diabetic retinopathy,9
E11321,9,E113219,"Type 2 diab with mild nonp rtnop with macular edema, unsp","Type 2 diabetes mellitus with mild nonproliferative diabetic retinopathy with macular edema, unspecified eye",Type 2 diabetes mellitus with mild nonproliferative diabetic retinopathy with macular edema,9
E11329,9,E113299,"Type 2 diab with mild nonp rtnop without macular edema, unsp","Type 2 diabetes mellitus with mild nonproliferative diabetic retinopathy without macular edema, unspecified eye",Type 2 diabetes mellitus with mild nonproliferative diabetic retinopathy without macular edema,9
E11331,9,E113319,"Type 2 diab with mod nonp rtnop with macular edema, unsp","Type 2 diabetes mellitus with moderate nonproliferative diabetic retinopathy with macular edema, unspecified eye",Type 2 diabetes mellitus with moderate nonproliferative diabetic retinopathy with macular edema,9
E11339,9,E113399,"Type 2 diab with mod nonp rtnop without macular edema, unsp","Type 2 diabetes mellitus with moderate nonproliferative diabetic retinopathy without macular edema, unspecified eye",Type 2 diabetes mellitus with moderate nonproliferative diabetic retinopathy without macular edema,9
E11341,9,E113419,"Type 2 diab with severe nonp rtnop with macular edema, unsp","Type 2 diabetes mellitus with severe nonproliferative diabetic retinopathy with macular edema, unspecified eye",Type 2 diabetes mellitus with severe nonproliferative diabetic retinopathy with macular edema,9
E11349,9,E113499,"Type 2 diab with severe nonp rtnop without mclr edema, unsp","Type 2 diabetes mellitus with severe nonproliferative diabetic retinopathy without macular edema, unspecified eye",Type 2 diabetes mellitus with severe nonproliferative diabetic retinopathy without macular edema,9
E11351,9,E113519,"Type 2 diab with prolif diab rtnop with macular edema, unsp","Type 2 diabetes mellitus with proliferative diabetic retinopathy with macular edema, unspecified eye",Type 2 diabetes mellitus with proliferative diabetic retinopathy with macular edema,9
E11352,9,E113529,"Type 2 diab w prolif diab rtnop with trctn dtch macula, unsp","Type 2 diabetes mellitus with proliferative diabetic retinopathy with traction retinal detachment involving the macula, unspecified eye",Type 2 diabetes mellitus with proliferative diabetic retinopathy with traction retinal detachment involving the macula,9
E11353,9,E113539,"Type 2 diab w prolif diab rtnop with trctn dtch n-mcla, unsp","Type 2 diabetes mellitus with proliferative diabetic retinopathy with traction retinal detachment not involving the macula, unspecified eye",Type 2 diabetes mellitus with proliferative diabetic retinopathy with traction retinal detachment not involving the macula,9
E11354,9,E113549,"Type 2 diab with prolif diab rtnop with comb detach, unsp","Type 2 diabetes mellitus with proliferative diabetic retinopathy with combined traction retinal detachment and rhegmatogenous retinal detachment, unspecified eye",Type 2 diabetes mellitus with proliferative diabetic retinopathy with combined traction retinal detachment and rhegmatogenous retinal detachment,9
E11355,9,E113559,"Type 2 diabetes with stable prolif diabetic rtnop, unsp","Type 2 diabetes mellitus with stable proliferative diabetic retinopathy, unspecified eye",Type 2 diabetes mellitus with stable proliferative diabetic retinopathy,9
E11359,9,E113599,"Type 2 diab with prolif diab rtnop without mclr edema, unsp","Type 2 diabetes mellitus with proliferative diabetic retinopathy without macular edema, unspecified eye",Type 2 diabetes mellitus with proliferative diabetic retinopathy without macular edema,9
E114,9,E1149,Type 2 diabetes w oth diabetic neurological complication,Type 2 diabetes mellitus with other diabetic neurological complication,Type 2 diabetes mellitus with neurological complications,9
E115,9,E1159,Type 2 diabetes mellitus with oth circulatory complications,Type 2 diabetes mellitus with other circulatory complications,Type 2 diabetes mellitus with circulatory complications,9
E1164,9,E11649,Type 2 diabetes mellitus with hypoglycemia without coma,Type 2 diabetes mellitus with hypoglycemia without coma,Type 2 diabetes mellitus with hypoglycemia,9
E132,9,E1329,Oth diabetes mellitus with oth diabetic kidney complication,Other specified diabetes mellitus with other diabetic kidney complication,Other specified diabetes mellitus with kidney complications,9
E1331,9,E13319,Oth diabetes w unsp diabetic retinopathy w/o macular edema,Other specified diabetes mellitus with unspecified diabetic retinopathy without macular edema,Other specified diabetes mellitus with unspecified diabetic retinopathy,9
E13321,9,E133219,"Oth diabetes with mild nonp rtnop with macular edema, unsp","Other specified diabetes mellitus with mild nonproliferative diabetic retinopathy with macular edema, unspecified eye",Other specified diabetes mellitus with mild nonproliferative diabetic retinopathy with macular edema,9
E13329,9,E133299,"Oth diab with mild nonp rtnop without macular edema, unsp","Other specified diabetes mellitus with mild nonproliferative diabetic retinopathy without macular edema, unspecified eye",Other specified diabetes mellitus with mild nonproliferative diabetic retinopathy without macular edema,9
E13331,9,E133319,"Oth diab with moderate nonp rtnop with macular edema, unsp","Other specified diabetes mellitus with moderate nonproliferative diabetic retinopathy with macular edema, unspecified eye",Other specified diabetes mellitus with moderate nonproliferative diabetic retinopathy with macular edema,9
E13339,9,E133399,"Oth diab with mod nonp rtnop without macular edema, unsp","Other specified diabetes mellitus with moderate nonproliferative diabetic retinopathy without macular edema, unspecified eye",Other specified diabetes mellitus with moderate nonproliferative diabetic retinopathy without macular edema,9
E13341,9,E133419,"Oth diabetes with severe nonp rtnop with macular edema, unsp","Other specified diabetes mellitus with severe nonproliferative diabetic retinopathy with macular edema, unspecified eye",Other specified diabetes mellitus with severe nonproliferative diabetic retinopathy with macular edema,9
E13349,9,E133499,"Oth diab with severe nonp rtnop without macular edema, unsp","Other specified diabetes mellitus with severe nonproliferative diabetic retinopathy without macular edema, unspecified eye",Other specified diabetes mellitus with severe nonproliferative diabetic retinopathy without macular edema,9
E13351,9,E133519,"Oth diab with prolif diabetic rtnop with macular edema, unsp","Other specified diabetes mellitus with proliferative diabetic retinopathy with macular edema, unspecified eye",Other specified diabetes mellitus with proliferative diabetic retinopathy with macular edema,9
E743,9,E7439,Other disorders of intestinal carbohydrate absorption,Other disorders of intestinal carbohydrate absorption,Other disorders of intestinal carbohydrate absorption,9
E13352,9,E133529,"Oth diab with prolif diab rtnop with trctn dtch macula, unsp","Other specified diabetes mellitus with proliferative diabetic retinopathy with traction retinal detachment involving the macula, unspecified eye",Other specified diabetes mellitus with proliferative diabetic retinopathy with traction retinal detachment involving the macula,9
E13353,9,E133539,"Oth diab with prolif diab rtnop with trctn dtch n-mcla, unsp","Other specified diabetes mellitus with proliferative diabetic retinopathy with traction retinal detachment not involving the macula, unspecified eye",Other specified diabetes mellitus with proliferative diabetic retinopathy with traction retinal detachment not involving the macula,9
E13354,9,E133549,"Oth diab with prolif diabetic rtnop with comb detach, unsp","Other specified diabetes mellitus with proliferative diabetic retinopathy with combined traction retinal detachment and rhegmatogenous retinal detachment, unspecified eye",Other specified diabetes mellitus with proliferative diabetic retinopathy with combined traction retinal detachment and rhegmatogenous retinal detachment,9
E13355,9,E133559,"Oth diabetes with stable prolif diabetic retinopathy, unsp","Other specified diabetes mellitus with stable proliferative diabetic retinopathy, unspecified eye",Other specified diabetes mellitus with stable proliferative diabetic retinopathy,9
E13359,9,E133599,"Oth diab with prolif diab rtnop without macular edema, unsp","Other specified diabetes mellitus with proliferative diabetic retinopathy without macular edema, unspecified eye",Other specified diabetes mellitus with proliferative diabetic retinopathy without macular edema,9
E134,9,E1349,Oth diabetes w oth diabetic neurological complication,Other specified diabetes mellitus with other diabetic neurological complication,Other specified diabetes mellitus with neurological complications,9
E135,9,E1359,Oth diabetes mellitus with other circulatory complications,Other specified diabetes mellitus with other circulatory complications,Other specified diabetes mellitus with circulatory complications,9
E1364,9,E13649,Oth diabetes mellitus with hypoglycemia without coma,Other specified diabetes mellitus with hypoglycemia without coma,Other specified diabetes mellitus with hypoglycemia,9
E16,9,E169,"Disorder of pancreatic internal secretion, unspecified","Disorder of pancreatic internal secretion, unspecified",Other disorders of pancreatic internal secretion,9
E20,9,E209,"Hypoparathyroidism, unspecified","Hypoparathyroidism, unspecified",Hypoparathyroidism,9
E22,9,E229,"Hyperfunction of pituitary gland, unspecified","Hyperfunction of pituitary gland, unspecified",Hyperfunction of pituitary gland,9
E24,9,E249,"Cushing''s syndrome, unspecified","Cushing''s syndrome, unspecified",Cushing's syndrome,9
E25,9,E259,"Adrenogenital disorder, unspecified","Adrenogenital disorder, unspecified",Adrenogenital disorders,9
E260,9,E2609,Other primary hyperaldosteronism,Other primary hyperaldosteronism,Primary hyperaldosteronism,9
E268,9,E2689,Other hyperaldosteronism,Other hyperaldosteronism,Other hyperaldosteronism,9
E274,9,E2749,Other adrenocortical insufficiency,Other adrenocortical insufficiency,Other and unspecified adrenocortical insufficiency,9
E2831,9,E28319,Asymptomatic premature menopause,Asymptomatic premature menopause,Premature menopause,9
E29,9,E299,"Testicular dysfunction, unspecified","Testicular dysfunction, unspecified",Testicular dysfunction,9
E30,9,E309,"Disorder of puberty, unspecified","Disorder of puberty, unspecified","Disorders of puberty, not elsewhere classified",9
E32,9,E329,"Disease of thymus, unspecified","Disease of thymus, unspecified",Diseases of thymus,9
E50,9,E509,"Vitamin A deficiency, unspecified","Vitamin A deficiency, unspecified",Vitamin A deficiency,9
E53,9,E539,"Vitamin B deficiency, unspecified","Vitamin B deficiency, unspecified",Deficiency of other B group vitamins,9
E55,9,E559,"Vitamin D deficiency, unspecified","Vitamin D deficiency, unspecified",Vitamin D deficiency,9
E56,9,E569,"Vitamin deficiency, unspecified","Vitamin deficiency, unspecified",Other vitamin deficiencies,9
E61,9,E619,"Deficiency of nutrient element, unspecified","Deficiency of nutrient element, unspecified",Deficiency of other nutrient elements,9
E63,9,E639,"Nutritional deficiency, unspecified","Nutritional deficiency, unspecified",Other nutritional deficiencies,9
E64,9,E649,Sequelae of unspecified nutritional deficiency,Sequelae of unspecified nutritional deficiency,Sequelae of malnutrition and other nutritional deficiencies,9
E660,9,E6609,Other obesity due to excess calories,Other obesity due to excess calories,Obesity due to excess calories,9
E702,9,E7029,Other disorders of tyrosine metabolism,Other disorders of tyrosine metabolism,Disorders of tyrosine metabolism,9
E7031,9,E70319,"Ocular albinism, unspecified","Ocular albinism, unspecified",Ocular albinism,9
E7032,9,E70329,"Oculocutaneous albinism, unspecified","Oculocutaneous albinism, unspecified",Oculocutaneous albinism,9
E7033,9,E70339,"Albinism with hematologic abnormality, unspecified","Albinism with hematologic abnormality, unspecified",Albinism with hematologic abnormality,9
E704,9,E7049,Other disorders of histidine metabolism,Other disorders of histidine metabolism,Disorders of histidine metabolism,9
E7152,9,E71529,"X-linked adrenoleukodystrophy, unspecified type","X-linked adrenoleukodystrophy, unspecified type",X-linked adrenoleukodystrophy,9
E720,9,E7209,Other disorders of amino-acid transport,Other disorders of amino-acid transport,Disorders of amino-acid transport,9
E721,9,E7219,Other disorders of sulfur-bearing amino-acid metabolism,Other disorders of sulfur-bearing amino-acid metabolism,Disorders of sulfur-bearing amino-acid metabolism,9
E722,9,E7229,Other disorders of urea cycle metabolism,Other disorders of urea cycle metabolism,Disorders of urea cycle metabolism,9
E725,9,E7259,Other disorders of glycine metabolism,Other disorders of glycine metabolism,Disorders of glycine metabolism,9
E73,9,E739,"Lactose intolerance, unspecified","Lactose intolerance, unspecified",Lactose intolerance,9
E740,9,E7409,Other glycogen storage disease,Other glycogen storage disease,Glycogen storage disease,9
E741,9,E7419,Other disorders of fructose metabolism,Other disorders of fructose metabolism,Disorders of fructose metabolism,9
E742,9,E7429,Other disorders of galactose metabolism,Other disorders of galactose metabolism,Disorders of galactose metabolism,9
E750,9,E7509,Other GM2 gangliosidosis,Other GM2 gangliosidosis,GM2 gangliosidosis,9
E7621,9,E76219,"Morquio mucopolysaccharidoses, unspecified","Morquio mucopolysaccharidoses, unspecified",Morquio mucopolysaccharidoses,9
E77,9,E779,"Disorder of glycoprotein metabolism, unspecified","Disorder of glycoprotein metabolism, unspecified",Disorders of glycoprotein metabolism,9
E787,9,E7879,Other disorders of bile acid and cholesterol metabolism,Other disorders of bile acid and cholesterol metabolism,Disorders of bile acid and cholesterol metabolism,9
E788,9,E7889,Other lipoprotein metabolism disorders,Other lipoprotein metabolism disorders,Other disorders of lipoprotein metabolism,9
E79,9,E799,"Disorder of purine and pyrimidine metabolism, unspecified","Disorder of purine and pyrimidine metabolism, unspecified",Disorders of purine and pyrimidine metabolism,9
E802,9,E8029,Other porphyria,Other porphyria,Other and unspecified porphyria,9
E830,9,E8309,Other disorders of copper metabolism,Other disorders of copper metabolism,Disorders of copper metabolism,9
E8311,9,E83119,"Hemochromatosis, unspecified","Hemochromatosis, unspecified",Hemochromatosis,9
E833,9,E8339,Other disorders of phosphorus metabolism,Other disorders of phosphorus metabolism,Disorders of phosphorus metabolism and phosphatases,9
E834,9,E8349,Other disorders of magnesium metabolism,Other disorders of magnesium metabolism,Disorders of magnesium metabolism,9
E835,9,E8359,Other disorders of calcium metabolism,Other disorders of calcium metabolism,Disorders of calcium metabolism,9
E838,9,E8389,Other disorders of mineral metabolism,Other disorders of mineral metabolism,Other disorders of mineral metabolism,9
E841,9,E8419,Cystic fibrosis with other intestinal manifestations,Cystic fibrosis with other intestinal manifestations,Cystic fibrosis with intestinal manifestations,9
E858,9,E8589,Other amyloidosis,Other amyloidosis,Other amyloidosis,9
E86,9,E869,"Volume depletion, unspecified","Volume depletion, unspecified",Volume depletion,9
E877,9,E8779,Other fluid overload,Other fluid overload,Fluid overload,9
E880,9,E8809,"Oth disorders of plasma-protein metabolism, NEC","Other disorders of plasma-protein metabolism, not elsewhere classified","Disorders of plasma-protein metabolism, not elsewhere classified",9
E884,9,E8849,Other mitochondrial metabolism disorders,Other mitochondrial metabolism disorders,Mitochondrial metabolism disorders,9
E888,9,E8889,Other specified metabolic disorders,Other specified metabolic disorders,Other specified metabolic disorders,9
F078,9,F0789,Oth personality & behavrl disord due to known physiol cond,Other personality and behavioral disorders due to known physiological condition,Other personality and behavioral disorders due to known physiological condition,9
F1012,9,F10129,"Alcohol abuse with intoxication, unspecified","Alcohol abuse with intoxication, unspecified",Alcohol abuse with intoxication,9
F1015,9,F10159,"Alcohol abuse with alcohol-induced psychotic disorder, unsp","Alcohol abuse with alcohol-induced psychotic disorder, unspecified",Alcohol abuse with alcohol-induced psychotic disorder,9
F1022,9,F10229,"Alcohol dependence with intoxication, unspecified","Alcohol dependence with intoxication, unspecified",Alcohol dependence with intoxication,9
F1023,9,F10239,"Alcohol dependence with withdrawal, unspecified","Alcohol dependence with withdrawal, unspecified",Alcohol dependence with withdrawal,9
F1025,9,F10259,"Alcohol dependence w alcoh-induce psychotic disorder, unsp","Alcohol dependence with alcohol-induced psychotic disorder, unspecified",Alcohol dependence with alcohol-induced psychotic disorder,9
F1092,9,F10929,"Alcohol use, unspecified with intoxication, unspecified","Alcohol use, unspecified with intoxication, unspecified","Alcohol use, unspecified with intoxication",9
F1095,9,F10959,"Alcohol use, unsp w alcohol-induced psychotic disorder, unsp","Alcohol use, unspecified with alcohol-induced psychotic disorder, unspecified","Alcohol use, unspecified with alcohol-induced psychotic disorder",9
F1112,9,F11129,"Opioid abuse with intoxication, unspecified","Opioid abuse with intoxication, unspecified",Opioid abuse with intoxication,9
F1115,9,F11159,"Opioid abuse with opioid-induced psychotic disorder, unsp","Opioid abuse with opioid-induced psychotic disorder, unspecified",Opioid abuse with opioid-induced psychotic disorder,9
F1122,9,F11229,"Opioid dependence with intoxication, unspecified","Opioid dependence with intoxication, unspecified",Opioid dependence with intoxication,9
F1125,9,F11259,"Opioid dependence w opioid-induced psychotic disorder, unsp","Opioid dependence with opioid-induced psychotic disorder, unspecified",Opioid dependence with opioid-induced psychotic disorder,9
F1192,9,F11929,"Opioid use, unspecified with intoxication, unspecified","Opioid use, unspecified with intoxication, unspecified","Opioid use, unspecified with intoxication",9
F1195,9,F11959,"Opioid use, unsp w opioid-induced psychotic disorder, unsp","Opioid use, unspecified with opioid-induced psychotic disorder, unspecified","Opioid use, unspecified with opioid-induced psychotic disorder",9
F1212,9,F12129,"Cannabis abuse with intoxication, unspecified","Cannabis abuse with intoxication, unspecified",Cannabis abuse with intoxication,9
F1215,9,F12159,"Cannabis abuse with psychotic disorder, unspecified","Cannabis abuse with psychotic disorder, unspecified",Cannabis abuse with psychotic disorder,9
F1222,9,F12229,"Cannabis dependence with intoxication, unspecified","Cannabis dependence with intoxication, unspecified",Cannabis dependence with intoxication,9
F1225,9,F12259,"Cannabis dependence with psychotic disorder, unspecified","Cannabis dependence with psychotic disorder, unspecified",Cannabis dependence with psychotic disorder,9
F1292,9,F12929,"Cannabis use, unspecified with intoxication, unspecified","Cannabis use, unspecified with intoxication, unspecified","Cannabis use, unspecified with intoxication",9
F1295,9,F12959,"Cannabis use, unsp with psychotic disorder, unspecified","Cannabis use, unspecified with psychotic disorder, unspecified","Cannabis use, unspecified with psychotic disorder",9
F1312,9,F13129,"Sedative, hypnotic or anxiolytic abuse w intoxication, unsp","Sedative, hypnotic or anxiolytic abuse with intoxication, unspecified","Sedative, hypnotic or anxiolytic abuse with intoxication",9
F1315,9,F13159,"Sedatv/hyp/anxiolytc abuse w psychotic disorder, unsp","Sedative, hypnotic or anxiolytic abuse with sedative, hypnotic or anxiolytic-induced psychotic disorder, unspecified","Sedative, hypnotic or anxiolytic abuse with sedative, hypnotic or anxiolytic-induced psychotic disorder",9
A329,0,A329,"Listeriosis, unspecified","Listeriosis, unspecified","Listeriosis, unspecified",9
F1322,9,F13229,"Sedatv/hyp/anxiolytc dependence w intoxication, unsp","Sedative, hypnotic or anxiolytic dependence with intoxication, unspecified","Sedative, hypnotic or anxiolytic dependence with intoxication",9
F1323,9,F13239,"Sedatv/hyp/anxiolytc dependence w withdrawal, unsp","Sedative, hypnotic or anxiolytic dependence with withdrawal, unspecified","Sedative, hypnotic or anxiolytic dependence with withdrawal",9
F1325,9,F13259,"Sedatv/hyp/anxiolytc dependence w psychotic disorder, unsp","Sedative, hypnotic or anxiolytic dependence with sedative, hypnotic or anxiolytic-induced psychotic disorder, unspecified","Sedative, hypnotic or anxiolytic dependence with sedative, hypnotic or anxiolytic-induced psychotic disorder",9
F1392,9,F13929,"Sedatv/hyp/anxiolytc use, unsp w intoxication, unsp","Sedative, hypnotic or anxiolytic use, unspecified with intoxication, unspecified","Sedative, hypnotic or anxiolytic use, unspecified with intoxication",9
F1393,9,F13939,"Sedatv/hyp/anxiolytc use, unsp w withdrawal, unsp","Sedative, hypnotic or anxiolytic use, unspecified with withdrawal, unspecified","Sedative, hypnotic or anxiolytic use, unspecified with withdrawal",9
F1395,9,F13959,"Sedatv/hyp/anxiolytc use, unsp w psychotic disorder, unsp","Sedative, hypnotic or anxiolytic use, unspecified with sedative, hypnotic or anxiolytic-induced psychotic disorder, unspecified","Sedative, hypnotic or anxiolytic use, unspecified with sedative, hypnotic or anxiolytic-induced psychotic disorder",9
F1412,9,F14129,"Cocaine abuse with intoxication, unspecified","Cocaine abuse with intoxication, unspecified",Cocaine abuse with intoxication,9
F1415,9,F14159,"Cocaine abuse with cocaine-induced psychotic disorder, unsp","Cocaine abuse with cocaine-induced psychotic disorder, unspecified",Cocaine abuse with cocaine-induced psychotic disorder,9
F1422,9,F14229,"Cocaine dependence with intoxication, unspecified","Cocaine dependence with intoxication, unspecified",Cocaine dependence with intoxication,9
F1425,9,F14259,"Cocaine dependence w cocaine-induc psychotic disorder, unsp","Cocaine dependence with cocaine-induced psychotic disorder, unspecified",Cocaine dependence with cocaine-induced psychotic disorder,9
F1492,9,F14929,"Cocaine use, unspecified with intoxication, unspecified","Cocaine use, unspecified with intoxication, unspecified","Cocaine use, unspecified with intoxication",9
F1495,9,F14959,"Cocaine use, unsp w cocaine-induced psychotic disorder, unsp","Cocaine use, unspecified with cocaine-induced psychotic disorder, unspecified","Cocaine use, unspecified with cocaine-induced psychotic disorder",9
F1512,9,F15129,"Other stimulant abuse with intoxication, unspecified","Other stimulant abuse with intoxication, unspecified",Other stimulant abuse with intoxication,9
F1515,9,F15159,"Oth stimulant abuse w stim-induce psychotic disorder, unsp","Other stimulant abuse with stimulant-induced psychotic disorder, unspecified",Other stimulant abuse with stimulant-induced psychotic disorder,9
F1522,9,F15229,"Other stimulant dependence with intoxication, unspecified","Other stimulant dependence with intoxication, unspecified",Other stimulant dependence with intoxication,9
F1525,9,F15259,"Oth stimulant depend w stim-induce psychotic disorder, unsp","Other stimulant dependence with stimulant-induced psychotic disorder, unspecified",Other stimulant dependence with stimulant-induced psychotic disorder,9
F1592,9,F15929,"Other stimulant use, unsp with intoxication, unspecified","Other stimulant use, unspecified with intoxication, unspecified","Other stimulant use, unspecified with intoxication",9
F1595,9,F15959,"Oth stimulant use, unsp w stim-induce psych disorder, unsp","Other stimulant use, unspecified with stimulant-induced psychotic disorder, unspecified","Other stimulant use, unspecified with stimulant-induced psychotic disorder",9
F1612,9,F16129,"Hallucinogen abuse with intoxication, unspecified","Hallucinogen abuse with intoxication, unspecified",Hallucinogen abuse with intoxication,9
F1615,9,F16159,"Hallucinogen abuse w psychotic disorder, unsp","Hallucinogen abuse with hallucinogen-induced psychotic disorder, unspecified",Hallucinogen abuse with hallucinogen-induced psychotic disorder,9
F1622,9,F16229,"Hallucinogen dependence with intoxication, unspecified","Hallucinogen dependence with intoxication, unspecified",Hallucinogen dependence with intoxication,9
F1625,9,F16259,"Hallucinogen dependence w psychotic disorder, unsp","Hallucinogen dependence with hallucinogen-induced psychotic disorder, unspecified",Hallucinogen dependence with hallucinogen-induced psychotic disorder,9
F1692,9,F16929,"Hallucinogen use, unspecified with intoxication, unspecified","Hallucinogen use, unspecified with intoxication, unspecified","Hallucinogen use, unspecified with intoxication",9
F1695,9,F16959,"Hallucinogen use, unsp w psychotic disorder, unsp","Hallucinogen use, unspecified with hallucinogen-induced psychotic disorder, unspecified","Hallucinogen use, unspecified with hallucinogen-induced psychotic disorder",9
F1720,9,F17209,"Nicotine dependence, unsp, w unsp nicotine-induced disorders","Nicotine dependence, unspecified, with unspecified nicotine-induced disorders","Nicotine dependence, unspecified",9
F1721,9,F17219,"Nicotine dependence, cigarettes, w unsp disorders","Nicotine dependence, cigarettes, with unspecified nicotine-induced disorders","Nicotine dependence, cigarettes",9
F1722,9,F17229,"Nicotine dependence, chewing tobacco, w unsp disorders","Nicotine dependence, chewing tobacco, with unspecified nicotine-induced disorders","Nicotine dependence, chewing tobacco",9
F1729,9,F17299,"Nicotine dependence, oth tobacco product, w unsp disorders","Nicotine dependence, other tobacco product, with unspecified nicotine-induced disorders","Nicotine dependence, other tobacco product",9
F1812,9,F18129,"Inhalant abuse with intoxication, unspecified","Inhalant abuse with intoxication, unspecified",Inhalant abuse with intoxication,9
F1815,9,F18159,"Inhalant abuse w inhalant-induced psychotic disorder, unsp","Inhalant abuse with inhalant-induced psychotic disorder, unspecified",Inhalant abuse with inhalant-induced psychotic disorder,9
F1822,9,F18229,"Inhalant dependence with intoxication, unspecified","Inhalant dependence with intoxication, unspecified",Inhalant dependence with intoxication,9
F1825,9,F18259,"Inhalant depend w inhalnt-induce psychotic disorder, unsp","Inhalant dependence with inhalant-induced psychotic disorder, unspecified",Inhalant dependence with inhalant-induced psychotic disorder,9
F1892,9,F18929,"Inhalant use, unspecified with intoxication, unspecified","Inhalant use, unspecified with intoxication, unspecified","Inhalant use, unspecified with intoxication",9
F1895,9,F18959,"Inhalant use, unsp w inhalnt-induce psychotic disorder, unsp","Inhalant use, unspecified with inhalant-induced psychotic disorder, unspecified","Inhalant use, unspecified with inhalant-induced psychotic disorder",9
F1912,9,F19129,"Other psychoactive substance abuse with intoxication, unsp","Other psychoactive substance abuse with intoxication, unspecified",Other psychoactive substance abuse with intoxication,9
F1915,9,F19159,"Oth psychoactive substance abuse w psychotic disorder, unsp","Other psychoactive substance abuse with psychoactive substance-induced psychotic disorder, unspecified",Other psychoactive substance abuse with psychoactive substance-induced psychotic disorder,9
F1922,9,F19229,"Oth psychoactive substance dependence w intoxication, unsp","Other psychoactive substance dependence with intoxication, unspecified",Other psychoactive substance dependence with intoxication,9
F1923,9,F19239,"Oth psychoactive substance dependence with withdrawal, unsp","Other psychoactive substance dependence with withdrawal, unspecified",Other psychoactive substance dependence with withdrawal,9
F1925,9,F19259,"Oth psychoactv substance depend w psychotic disorder, unsp","Other psychoactive substance dependence with psychoactive substance-induced psychotic disorder, unspecified",Other psychoactive substance dependence with psychoactive substance-induced psychotic disorder,9
F1992,9,F19929,"Oth psychoactive substance use, unsp with intoxication, unsp","Other psychoactive substance use, unspecified with intoxication, unspecified","Other psychoactive substance use, unspecified with intoxication",9
F1993,9,F19939,"Other psychoactive substance use, unsp with withdrawal, unsp","Other psychoactive substance use, unspecified with withdrawal, unspecified","Other psychoactive substance use, unspecified with withdrawal",9
F1995,9,F19959,"Oth psychoactv substance use, unsp w psych disorder, unsp","Other psychoactive substance use, unspecified with psychoactive substance-induced psychotic disorder, unspecified","Other psychoactive substance use, unspecified with psychoactive substance-induced psychotic disorder",9
F208,9,F2089,Other schizophrenia,Other schizophrenia,Other schizophrenia,9
F25,9,F259,"Schizoaffective disorder, unspecified","Schizoaffective disorder, unspecified",Schizoaffective disorders,9
F318,9,F3189,Other bipolar disorder,Other bipolar disorder,Other bipolar disorders,9
F328,9,F3289,Other specified depressive episodes,Other specified depressive episodes,Other depressive episodes,9
F348,9,F3489,Other specified persistent mood disorders,Other specified persistent mood disorders,Other persistent mood [affective] disorders,9
F41,9,F419,"Anxiety disorder, unspecified","Anxiety disorder, unspecified",Other anxiety disorders,9
F42,9,F429,"Obsessive-compulsive disorder, unspecified","Obsessive-compulsive disorder, unspecified",Obsessive-compulsive disorder,9
F432,9,F4329,Adjustment disorder with other symptoms,Adjustment disorder with other symptoms,Adjustment disorders,9
F448,9,F4489,Other dissociative and conversion disorders,Other dissociative and conversion disorders,Other dissociative and conversion disorders,9
F452,9,F4529,Other hypochondriacal disorders,Other hypochondriacal disorders,Hypochondriacal disorders,9
F48,9,F489,"Nonpsychotic mental disorder, unspecified","Nonpsychotic mental disorder, unspecified",Other nonpsychotic mental disorders,9
F508,9,F5089,Other specified eating disorder,Other specified eating disorder,Other eating disorders,9
F510,9,F5109,Oth insomnia not due to a substance or known physiol cond,Other insomnia not due to a substance or known physiological condition,Insomnia not due to a substance or known physiological condition,9
F511,9,F5119,Oth hypersomnia not due to a substance or known physiol cond,Other hypersomnia not due to a substance or known physiological condition,Hypersomnia not due to a substance or known physiological condition,9
F608,9,F6089,Other specific personality disorders,Other specific personality disorders,Other specific personality disorders,9
F638,9,F6389,Other impulse disorders,Other impulse disorders,Other impulse disorders,9
F64,9,F649,"Gender identity disorder, unspecified","Gender identity disorder, unspecified",Gender identity disorders,9
F658,9,F6589,Other paraphilias,Other paraphilias,Other paraphilias,9
F808,9,F8089,Other developmental disorders of speech and language,Other developmental disorders of speech and language,Other developmental disorders of speech and language,9
F818,9,F8189,Other developmental disorders of scholastic skills,Other developmental disorders of scholastic skills,Other developmental disorders of scholastic skills,9
F84,9,F849,"Pervasive developmental disorder, unspecified","Pervasive developmental disorder, unspecified",Pervasive developmental disorders,9
F90,9,F909,"Attention-deficit hyperactivity disorder, unspecified type","Attention-deficit hyperactivity disorder, unspecified type",Attention-deficit hyperactivity disorders,9
F91,9,F919,"Conduct disorder, unspecified","Conduct disorder, unspecified",Conduct disorders,9
F93,9,F939,"Childhood emotional disorder, unspecified","Childhood emotional disorder, unspecified",Emotional disorders with onset specific to childhood,9
F94,9,F949,"Childhood disorder of social functioning, unspecified","Childhood disorder of social functioning, unspecified",Disorders of social functioning with onset specific to childhood and adolescence,9
F95,9,F959,"Tic disorder, unspecified","Tic disorder, unspecified",Tic disorder,9
F982,9,F9829,Other feeding disorders of infancy and early childhood,Other feeding disorders of infancy and early childhood,Other feeding disorders of infancy and childhood,9
G00,9,G009,"Bacterial meningitis, unspecified","Bacterial meningitis, unspecified","Bacterial meningitis, not elsewhere classified",9
G03,9,G039,"Meningitis, unspecified","Meningitis, unspecified",Meningitis due to other and unspecified causes,9
G043,9,G0439,Other acute necrotizing hemorrhagic encephalopathy,Other acute necrotizing hemorrhagic encephalopathy,Acute necrotizing hemorrhagic encephalopathy,9
G048,9,G0489,Other myelitis,Other myelitis,"Other encephalitis, myelitis and encephalomyelitis",9
G11,9,G119,"Hereditary ataxia, unspecified","Hereditary ataxia, unspecified",Hereditary ataxia,9
G122,9,G1229,Other motor neuron disease,Other motor neuron disease,Motor neuron disease,9
G211,9,G2119,Other drug induced secondary parkinsonism,Other drug induced secondary parkinsonism,Other drug-induced secondary parkinsonism,9
G23,9,G239,"Degenerative disease of basal ganglia, unspecified","Degenerative disease of basal ganglia, unspecified",Other degenerative diseases of basal ganglia,9
G240,9,G2409,Other drug induced dystonia,Other drug induced dystonia,Drug induced dystonia,9
G256,9,G2569,Other tics of organic origin,Other tics of organic origin,Drug induced tics and other tics of organic origin,9
G257,9,G2579,Other drug induced movement disorders,Other drug induced movement disorders,Other and unspecified drug induced movement disorders,9
G258,9,G2589,Other specified extrapyramidal and movement disorders,Other specified extrapyramidal and movement disorders,Other specified extrapyramidal and movement disorders,9
G30,9,G309,"Alzheimer''s disease, unspecified","Alzheimer''s disease, unspecified",Alzheimer's disease,9
G310,9,G3109,Other frontotemporal dementia,Other frontotemporal dementia,Frontotemporal dementia,9
G318,9,G3189,Other specified degenerative diseases of nervous system,Other specified degenerative diseases of nervous system,Other specified degenerative diseases of nervous system,9
G328,9,G3289,Oth degeneratv disord of nervous sys in dis classd elswhr,Other specified degenerative disorders of nervous system in diseases classified elsewhere,Other specified degenerative disorders of nervous system in diseases classified elsewhere,9
G36,9,G369,"Acute disseminated demyelination, unspecified","Acute disseminated demyelination, unspecified",Other acute disseminated demyelination,9
G37,9,G379,"Demyelinating disease of central nervous system, unspecified","Demyelinating disease of central nervous system, unspecified",Other demyelinating diseases of central nervous system,9
G4000,9,G40009,"Local-rel idio epi w seiz of loc onst,not ntrct,w/o stat epi","Localization-related (focal) (partial) idiopathic epilepsy and epileptic syndromes with seizures of localized onset, not intractable, without status epilepticus","Localization-related (focal) (partial) idiopathic epilepsy and epileptic syndromes with seizures of localized onset, not intractable",9
G4001,9,G40019,"Local-rel idio epi w seiz of loc onset, ntrct, w/o stat epi","Localization-related (focal) (partial) idiopathic epilepsy and epileptic syndromes with seizures of localized onset, intractable, without status epilepticus","Localization-related (focal) (partial) idiopathic epilepsy and epileptic syndromes with seizures of localized onset, intractable",9
G4010,9,G40109,"Local-rel symptc epi w simp prt seiz,not ntrct, w/o stat epi","Localization-related (focal) (partial) symptomatic epilepsy and epileptic syndromes with simple partial seizures, not intractable, without status epilepticus","Localization-related (focal) (partial) symptomatic epilepsy and epileptic syndromes with simple partial seizures, not intractable",9
G4011,9,G40119,"Local-rel symptc epi w simple part seiz, ntrct, w/o stat epi","Localization-related (focal) (partial) symptomatic epilepsy and epileptic syndromes with simple partial seizures, intractable, without status epilepticus","Localization-related (focal) (partial) symptomatic epilepsy and epileptic syndromes with simple partial seizures, intractable",9
G4020,9,G40209,"Local-rel symptc epi w cmplx prt seiz,not ntrct,w/o stat epi","Localization-related (focal) (partial) symptomatic epilepsy and epileptic syndromes with complex partial seizures, not intractable, without status epilepticus","Localization-related (focal) (partial) symptomatic epilepsy and epileptic syndromes with complex partial seizures, not intractable",9
G4021,9,G40219,"Local-rel symptc epi w cmplx part seiz, ntrct, w/o stat epi","Localization-related (focal) (partial) symptomatic epilepsy and epileptic syndromes with complex partial seizures, intractable, without status epilepticus","Localization-related (focal) (partial) symptomatic epilepsy and epileptic syndromes with complex partial seizures, intractable",9
G4030,9,G40309,"Gen idiopathic epilepsy, not intractable, w/o stat epi","Generalized idiopathic epilepsy and epileptic syndromes, not intractable, without status epilepticus","Generalized idiopathic epilepsy and epileptic syndromes, not intractable",9
G4031,9,G40319,"Generalized idiopathic epilepsy, intractable, w/o stat epi","Generalized idiopathic epilepsy and epileptic syndromes, intractable, without status epilepticus","Generalized idiopathic epilepsy and epileptic syndromes, intractable",9
G40A0,9,G40A09,"Absence epileptic syndrome, not intractable, w/o stat epi","Absence epileptic syndrome, not intractable, without status epilepticus","Absence epileptic syndrome, not intractable",9
G40A1,9,G40A19,"Absence epileptic syndrome, intractable, w/o stat epi","Absence epileptic syndrome, intractable, without status epilepticus","Absence epileptic syndrome, intractable",9
G40B0,9,G40B09,"Juvenile myoclonic epilepsy, not intractable, w/o stat epi","Juvenile myoclonic epilepsy, not intractable, without status epilepticus","Juvenile myoclonic epilepsy, not intractable",9
G40B1,9,G40B19,"Juvenile myoclonic epilepsy, intractable, w/o stat epi","Juvenile myoclonic epilepsy, intractable, without status epilepticus","Juvenile myoclonic epilepsy, intractable",9
G4040,9,G40409,"Oth generalized epilepsy, not intractable, w/o stat epi","Other generalized epilepsy and epileptic syndromes, not intractable, without status epilepticus","Other generalized epilepsy and epileptic syndromes, not intractable",9
G4041,9,G40419,"Oth generalized epilepsy, intractable, w/o stat epi","Other generalized epilepsy and epileptic syndromes, intractable, without status epilepticus","Other generalized epilepsy and epileptic syndromes, intractable",9
G4050,9,G40509,"Epileptic seiz rel to extrn causes, not ntrct, w/o stat epi","Epileptic seizures related to external causes, not intractable, without status epilepticus","Epileptic seizures related to external causes, not intractable",9
G4090,9,G40909,"Epilepsy, unsp, not intractable, without status epilepticus","Epilepsy, unspecified, not intractable, without status epilepticus","Epilepsy, unspecified, not intractable",9
G4091,9,G40919,"Epilepsy, unsp, intractable, without status epilepticus","Epilepsy, unspecified, intractable, without status epilepticus","Epilepsy, unspecified, intractable",9
G4300,9,G43009,"Migraine w/o aura, not intractable, w/o status migrainosus","Migraine without aura, not intractable, without status migrainosus","Migraine without aura, not intractable",9
G4301,9,G43019,"Migraine w/o aura, intractable, without status migrainosus","Migraine without aura, intractable, without status migrainosus","Migraine without aura, intractable",9
G4310,9,G43109,"Migraine with aura, not intractable, w/o status migrainosus","Migraine with aura, not intractable, without status migrainosus","Migraine with aura, not intractable",9
G4311,9,G43119,"Migraine with aura, intractable, without status migrainosus","Migraine with aura, intractable, without status migrainosus","Migraine with aura, intractable",9
G4340,9,G43409,"Hemiplegic migraine, not intractable, w/o status migrainosus","Hemiplegic migraine, not intractable, without status migrainosus","Hemiplegic migraine, not intractable",9
G4341,9,G43419,"Hemiplegic migraine, intractable, without status migrainosus","Hemiplegic migraine, intractable, without status migrainosus","Hemiplegic migraine, intractable",9
G4350,9,G43509,"Perst migrn aura w/o cereb infrc, not ntrct, w/o stat migr","Persistent migraine aura without cerebral infarction, not intractable, without status migrainosus","Persistent migraine aura without cerebral infarction, not intractable",9
G4351,9,G43519,"Perst migraine aura w/o cerebral infrc, ntrct, w/o stat migr","Persistent migraine aura without cerebral infarction, intractable, without status migrainosus","Persistent migraine aura without cerebral infarction, intractable",9
G4360,9,G43609,"Perst migraine aura w cereb infrc, not ntrct, w/o stat migr","Persistent migraine aura with cerebral infarction, not intractable, without status migrainosus","Persistent migraine aura with cerebral infarction, not intractable",9
G4361,9,G43619,"Perst migraine aura w cerebral infrc, ntrct, w/o stat migr","Persistent migraine aura with cerebral infarction, intractable, without status migrainosus","Persistent migraine aura with cerebral infarction, intractable",9
G4370,9,G43709,"Chronic migraine w/o aura, not intractable, w/o stat migr","Chronic migraine without aura, not intractable, without status migrainosus","Chronic migraine without aura, not intractable",9
G4371,9,G43719,"Chronic migraine w/o aura, intractable, w/o stat migr","Chronic migraine without aura, intractable, without status migrainosus","Chronic migraine without aura, intractable",9
G4380,9,G43809,"Other migraine, not intractable, without status migrainosus","Other migraine, not intractable, without status migrainosus","Other migraine, not intractable",9
G4381,9,G43819,"Other migraine, intractable, without status migrainosus","Other migraine, intractable, without status migrainosus","Other migraine, intractable",9
G4382,9,G43829,"Menstrual migraine, not intractable, w/o status migrainosus","Menstrual migraine, not intractable, without status migrainosus","Menstrual migraine, not intractable",9
G4383,9,G43839,"Menstrual migraine, intractable, without status migrainosus","Menstrual migraine, intractable, without status migrainosus","Menstrual migraine, intractable",9
G4390,9,G43909,"Migraine, unsp, not intractable, without status migrainosus","Migraine, unspecified, not intractable, without status migrainosus","Migraine, unspecified, not intractable",9
G4391,9,G43919,"Migraine, unsp, intractable, without status migrainosus","Migraine, unspecified, intractable, without status migrainosus","Migraine, unspecified, intractable",9
G4400,9,G44009,"Cluster headache syndrome, unspecified, not intractable","Cluster headache syndrome, unspecified, not intractable","Cluster headache syndrome, unspecified",9
G4401,9,G44019,"Episodic cluster headache, not intractable","Episodic cluster headache, not intractable",Episodic cluster headache,9
G4402,9,G44029,"Chronic cluster headache, not intractable","Chronic cluster headache, not intractable",Chronic cluster headache,9
G4403,9,G44039,"Episodic paroxysmal hemicrania, not intractable","Episodic paroxysmal hemicrania, not intractable",Episodic paroxysmal hemicrania,9
G4404,9,G44049,"Chronic paroxysmal hemicrania, not intractable","Chronic paroxysmal hemicrania, not intractable",Chronic paroxysmal hemicrania,9
G4405,9,G44059,"Shrt lst unil nerlgif hdache w cnjnct inject/tear, not ntrct","Short lasting unilateral neuralgiform headache with conjunctival injection and tearing (SUNCT), not intractable",Short lasting unilateral neuralgiform headache with conjunctival injection and tearing (SUNCT),9
G4409,9,G44099,"Other trigeminal autonomic cephalgias (TAC), not intractable","Other trigeminal autonomic cephalgias (TAC), not intractable",Other trigeminal autonomic cephalgias (TAC),9
G4420,9,G44209,"Tension-type headache, unspecified, not intractable","Tension-type headache, unspecified, not intractable","Tension-type headache, unspecified",9
G4421,9,G44219,"Episodic tension-type headache, not intractable","Episodic tension-type headache, not intractable",Episodic tension-type headache,9
G4422,9,G44229,"Chronic tension-type headache, not intractable","Chronic tension-type headache, not intractable",Chronic tension-type headache,9
G4430,9,G44309,"Post-traumatic headache, unspecified, not intractable","Post-traumatic headache, unspecified, not intractable","Post-traumatic headache, unspecified",9
G4431,9,G44319,"Acute post-traumatic headache, not intractable","Acute post-traumatic headache, not intractable",Acute post-traumatic headache,9
G4432,9,G44329,"Chronic post-traumatic headache, not intractable","Chronic post-traumatic headache, not intractable",Chronic post-traumatic headache,9
G445,9,G4459,Other complicated headache syndrome,Other complicated headache syndrome,Complicated headache syndromes,9
G448,9,G4489,Other headache syndrome,Other headache syndrome,Other specified headache syndromes,9
G45,9,G459,"Transient cerebral ischemic attack, unspecified","Transient cerebral ischemic attack, unspecified",Transient cerebral ischemic attacks and related syndromes,9
G470,9,G4709,Other insomnia,Other insomnia,Insomnia,9
G471,9,G4719,Other hypersomnia,Other hypersomnia,Hypersomnia,9
G472,9,G4729,Other circadian rhythm sleep disorder,Other circadian rhythm sleep disorder,Circadian rhythm sleep disorders,9
G473,9,G4739,Other sleep apnea,Other sleep apnea,Sleep apnea,9
G4741,9,G47419,Narcolepsy without cataplexy,Narcolepsy without cataplexy,Narcolepsy,9
G4742,9,G47429,Narcolepsy in conditions classified elsewhere w/o cataplexy,Narcolepsy in conditions classified elsewhere without cataplexy,Narcolepsy in conditions classified elsewhere,9
G475,9,G4759,Other parasomnia,Other parasomnia,Parasomnia,9
G476,9,G4769,Other sleep related movement disorders,Other sleep related movement disorders,Sleep related movement disorders,9
G50,9,G509,"Disorder of trigeminal nerve, unspecified","Disorder of trigeminal nerve, unspecified",Disorders of trigeminal nerve,9
G51,9,G519,"Disorder of facial nerve, unspecified","Disorder of facial nerve, unspecified",Facial nerve disorders,9
G52,9,G529,"Cranial nerve disorder, unspecified","Cranial nerve disorder, unspecified",Disorders of other cranial nerves,9
G54,9,G549,"Nerve root and plexus disorder, unspecified","Nerve root and plexus disorder, unspecified",Nerve root and plexus disorders,9
E0837,0,E0837X1,"Diab with diabetic macular edema, resolved fol trtmt, r eye","Diabetes mellitus due to underlying condition with diabetic macular edema, resolved following treatment, right eye","Diabetes mellitus due to underlying condition with diabetic macular edema, resolved following treatment",9
A33,0,A33,Tetanus neonatorum,Tetanus neonatorum,Tetanus neonatorum,9
A34,0,A34,Obstetrical tetanus,Obstetrical tetanus,Obstetrical tetanus,9
E0937,0,E0937X1,"Drug/chem diab w diab mclr edma, resolved fol trtmt, r eye","Drug or chemical induced diabetes mellitus with diabetic macular edema, resolved following treatment, right eye","Drug or chemical induced diabetes mellitus with diabetic macular edema, resolved following treatment",9
E1037,0,E1037X1,"Type 1 diab with diab mclr edema, resolved fol trtmt, r eye","Type 1 diabetes mellitus with diabetic macular edema, resolved following treatment, right eye","Type 1 diabetes mellitus with diabetic macular edema, resolved following treatment",9
E1137,0,E1137X1,"Type 2 diab with diab mclr edema, resolved fol trtmt, r eye","Type 2 diabetes mellitus with diabetic macular edema, resolved following treatment, right eye","Type 2 diabetes mellitus with diabetic macular edema, resolved following treatment",9
E1337,0,E1337X1,"Oth diab with diab macular edema, resolved fol trtmt, r eye","Other specified diabetes mellitus with diabetic macular edema, resolved following treatment, right eye","Other specified diabetes mellitus with diabetic macular edema, resolved following treatment",9
E0837,0,E0837X2,"Diab with diab macular edema, resolved fol trtmt, left eye","Diabetes mellitus due to underlying condition with diabetic macular edema, resolved following treatment, left eye","Diabetes mellitus due to underlying condition with diabetic macular edema, resolved following treatment",9
E0937,0,E0937X2,"Drug/chem diab w diab mclr edma, resolved fol trtmt, l eye","Drug or chemical induced diabetes mellitus with diabetic macular edema, resolved following treatment, left eye","Drug or chemical induced diabetes mellitus with diabetic macular edema, resolved following treatment",9
E1037,0,E1037X2,"Type 1 diab with diab mclr edema, resolved fol trtmt, l eye","Type 1 diabetes mellitus with diabetic macular edema, resolved following treatment, left eye","Type 1 diabetes mellitus with diabetic macular edema, resolved following treatment",9
E1137,0,E1137X2,"Type 2 diab with diab mclr edema, resolved fol trtmt, l eye","Type 2 diabetes mellitus with diabetic macular edema, resolved following treatment, left eye","Type 2 diabetes mellitus with diabetic macular edema, resolved following treatment",9
E1337,0,E1337X2,"Oth diab with diab macular edema, resolved fol trtmt, l eye","Other specified diabetes mellitus with diabetic macular edema, resolved following treatment, left eye","Other specified diabetes mellitus with diabetic macular edema, resolved following treatment",9
E0837,0,E0837X3,"Diabetes with diabetic macular edema, resolved fol trtmt, bi","Diabetes mellitus due to underlying condition with diabetic macular edema, resolved following treatment, bilateral","Diabetes mellitus due to underlying condition with diabetic macular edema, resolved following treatment",9
E0937,0,E0937X3,"Drug/chem diab with diab mclr edema, resolved fol trtmt, bi","Drug or chemical induced diabetes mellitus with diabetic macular edema, resolved following treatment, bilateral","Drug or chemical induced diabetes mellitus with diabetic macular edema, resolved following treatment",9
E1037,0,E1037X3,"Type 1 diab with diab macular edema, resolved fol trtmt, bi","Type 1 diabetes mellitus with diabetic macular edema, resolved following treatment, bilateral","Type 1 diabetes mellitus with diabetic macular edema, resolved following treatment",9
E1137,0,E1137X3,"Type 2 diab with diab macular edema, resolved fol trtmt, bi","Type 2 diabetes mellitus with diabetic macular edema, resolved following treatment, bilateral","Type 2 diabetes mellitus with diabetic macular edema, resolved following treatment",9
E1337,0,E1337X3,"Oth diab with diabetic macular edema, resolved fol trtmt, bi","Other specified diabetes mellitus with diabetic macular edema, resolved following treatment, bilateral","Other specified diabetes mellitus with diabetic macular edema, resolved following treatment",9
E0837,0,E0837X9,"Diab with diabetic macular edema, resolved fol trtmt, unsp","Diabetes mellitus due to underlying condition with diabetic macular edema, resolved following treatment, unspecified eye","Diabetes mellitus due to underlying condition with diabetic macular edema, resolved following treatment",9
E0937,0,E0937X9,"Drug/chem diab with diab mclr edma, resolved fol trtmt, unsp","Drug or chemical induced diabetes mellitus with diabetic macular edema, resolved following treatment, unspecified eye","Drug or chemical induced diabetes mellitus with diabetic macular edema, resolved following treatment",9
E1037,0,E1037X9,"Type 1 diab with diab mclr edema, resolved fol trtmt, unsp","Type 1 diabetes mellitus with diabetic macular edema, resolved following treatment, unspecified eye","Type 1 diabetes mellitus with diabetic macular edema, resolved following treatment",9
E1137,0,E1137X9,"Type 2 diab with diab mclr edema, resolved fol trtmt, unsp","Type 2 diabetes mellitus with diabetic macular edema, resolved following treatment, unspecified eye","Type 2 diabetes mellitus with diabetic macular edema, resolved following treatment",9
E1337,0,E1337X9,"Oth diab with diab macular edema, resolved fol trtmt, unsp","Other specified diabetes mellitus with diabetic macular edema, resolved following treatment, unspecified eye","Other specified diabetes mellitus with diabetic macular edema, resolved following treatment",9
A048,0,A048,Other specified bacterial intestinal infections,Other specified bacterial intestinal infections,Other specified bacterial intestinal infections,9
A049,0,A049,"Bacterial intestinal infection, unspecified","Bacterial intestinal infection, unspecified","Bacterial intestinal infection, unspecified",9
A069,0,A069,"Amebiasis, unspecified","Amebiasis, unspecified","Amebiasis, unspecified",9
A082,0,A082,Adenoviral enteritis,Adenoviral enteritis,Adenoviral enteritis,9
A084,0,A084,"Viral intestinal infection, unspecified","Viral intestinal infection, unspecified","Viral intestinal infection, unspecified",9
A088,0,A088,Other specified intestinal infections,Other specified intestinal infections,Other specified intestinal infections,9
A09,0,A09,"Infectious gastroenteritis and colitis, unspecified","Infectious gastroenteritis and colitis, unspecified","Infectious gastroenteritis and colitis, unspecified",9
A179,0,A179,"Tuberculosis of nervous system, unspecified","Tuberculosis of nervous system, unspecified","Tuberculosis of nervous system, unspecified",9
A182,0,A182,Tuberculous peripheral lymphadenopathy,Tuberculous peripheral lymphadenopathy,Tuberculous peripheral lymphadenopathy,9
A184,0,A184,Tuberculosis of skin and subcutaneous tissue,Tuberculosis of skin and subcutaneous tissue,Tuberculosis of skin and subcutaneous tissue,9
A186,0,A186,Tuberculosis of (inner) (middle) ear,Tuberculosis of (inner) (middle) ear,Tuberculosis of (inner) (middle) ear,9
A187,0,A187,Tuberculosis of adrenal glands,Tuberculosis of adrenal glands,Tuberculosis of adrenal glands,9
A279,0,A279,"Leptospirosis, unspecified","Leptospirosis, unspecified","Leptospirosis, unspecified",9
A327,0,A327,Listerial sepsis,Listerial sepsis,Listerial sepsis,9
A399,0,A399,"Meningococcal infection, unspecified","Meningococcal infection, unspecified","Meningococcal infection, unspecified",9
A411,0,A411,Sepsis due to other specified staphylococcus,Sepsis due to other specified staphylococcus,Sepsis due to other specified staphylococcus,9
A412,0,A412,Sepsis due to unspecified staphylococcus,Sepsis due to unspecified staphylococcus,Sepsis due to unspecified staphylococcus,9
A413,0,A413,Sepsis due to Hemophilus influenzae,Sepsis due to Hemophilus influenzae,Sepsis due to Hemophilus influenzae,9
A414,0,A414,Sepsis due to anaerobes,Sepsis due to anaerobes,Sepsis due to anaerobes,9
A419,0,A419,"Sepsis, unspecified organism","Sepsis, unspecified organism","Sepsis, unspecified organism",9
A429,0,A429,"Actinomycosis, unspecified","Actinomycosis, unspecified","Actinomycosis, unspecified",9
A46,0,A46,Erysipelas,Erysipelas,Erysipelas,9
A488,0,A488,Other specified bacterial diseases,Other specified bacterial diseases,Other specified bacterial diseases,9
A491,0,A491,"Streptococcal infection, unspecified site","Streptococcal infection, unspecified site","Streptococcal infection, unspecified site",9
A492,0,A492,"Hemophilus influenzae infection, unspecified site","Hemophilus influenzae infection, unspecified site","Hemophilus influenzae infection, unspecified site",9
A493,0,A493,"Mycoplasma infection, unspecified site","Mycoplasma infection, unspecified site","Mycoplasma infection, unspecified site",9
A498,0,A498,Other bacterial infections of unspecified site,Other bacterial infections of unspecified site,Other bacterial infections of unspecified site,9
A499,0,A499,"Bacterial infection, unspecified","Bacterial infection, unspecified","Bacterial infection, unspecified",9
A501,0,A501,"Early congenital syphilis, latent","Early congenital syphilis, latent","Early congenital syphilis, latent",9
A502,0,A502,"Early congenital syphilis, unspecified","Early congenital syphilis, unspecified","Early congenital syphilis, unspecified",9
A506,0,A506,"Late congenital syphilis, latent","Late congenital syphilis, latent","Late congenital syphilis, latent",9
A507,0,A507,"Late congenital syphilis, unspecified","Late congenital syphilis, unspecified","Late congenital syphilis, unspecified",9
A509,0,A509,"Congenital syphilis, unspecified","Congenital syphilis, unspecified","Congenital syphilis, unspecified",9
A515,0,A515,"Early syphilis, latent","Early syphilis, latent","Early syphilis, latent",9
A519,0,A519,"Early syphilis, unspecified","Early syphilis, unspecified","Early syphilis, unspecified",9
A522,0,A522,Asymptomatic neurosyphilis,Asymptomatic neurosyphilis,Asymptomatic neurosyphilis,9
A523,0,A523,"Neurosyphilis, unspecified","Neurosyphilis, unspecified","Neurosyphilis, unspecified",9
A528,0,A528,"Late syphilis, latent","Late syphilis, latent","Late syphilis, latent",9
A529,0,A529,"Late syphilis, unspecified","Late syphilis, unspecified","Late syphilis, unspecified",9
A541,0,A541,Gonocl infct of lower GU tract w periureth and acc glnd abcs,Gonococcal infection of lower genitourinary tract with periurethral and accessory gland abscess,Gonococcal infection of lower genitourinary tract with periurethral and accessory gland abscess,9
A545,0,A545,Gonococcal pharyngitis,Gonococcal pharyngitis,Gonococcal pharyngitis,9
A546,0,A546,Gonococcal infection of anus and rectum,Gonococcal infection of anus and rectum,Gonococcal infection of anus and rectum,9
A549,0,A549,"Gonococcal infection, unspecified","Gonococcal infection, unspecified","Gonococcal infection, unspecified",9
A55,0,A55,Chlamydial lymphogranuloma (venereum),Chlamydial lymphogranuloma (venereum),Chlamydial lymphogranuloma (venereum),9
A562,0,A562,"Chlamydial infection of genitourinary tract, unspecified","Chlamydial infection of genitourinary tract, unspecified","Chlamydial infection of genitourinary tract, unspecified",9
A563,0,A563,Chlamydial infection of anus and rectum,Chlamydial infection of anus and rectum,Chlamydial infection of anus and rectum,9
A564,0,A564,Chlamydial infection of pharynx,Chlamydial infection of pharynx,Chlamydial infection of pharynx,9
A568,0,A568,Sexually transmitted chlamydial infection of other sites,Sexually transmitted chlamydial infection of other sites,Sexually transmitted chlamydial infection of other sites,9
A57,0,A57,Chancroid,Chancroid,Chancroid,9
A58,0,A58,Granuloma inguinale,Granuloma inguinale,Granuloma inguinale,9
A598,0,A598,Trichomoniasis of other sites,Trichomoniasis of other sites,Trichomoniasis of other sites,9
A599,0,A599,"Trichomoniasis, unspecified","Trichomoniasis, unspecified","Trichomoniasis, unspecified",9
A601,0,A601,Herpesviral infection of perianal skin and rectum,Herpesviral infection of perianal skin and rectum,Herpesviral infection of perianal skin and rectum,9
A609,0,A609,"Anogenital herpesviral infection, unspecified","Anogenital herpesviral infection, unspecified","Anogenital herpesviral infection, unspecified",9
A64,0,A64,Unspecified sexually transmitted disease,Unspecified sexually transmitted disease,Unspecified sexually transmitted disease,9
A65,0,A65,Nonvenereal syphilis,Nonvenereal syphilis,Nonvenereal syphilis,9
A698,0,A698,Other specified spirochetal infections,Other specified spirochetal infections,Other specified spirochetal infections,9
A699,0,A699,"Spirochetal infection, unspecified","Spirochetal infection, unspecified","Spirochetal infection, unspecified",9
A70,0,A70,Chlamydia psittaci infections,Chlamydia psittaci infections,Chlamydia psittaci infections,9
A749,0,A749,"Chlamydial infection, unspecified","Chlamydial infection, unspecified","Chlamydial infection, unspecified",9
A778,0,A778,Other spotted fevers,Other spotted fevers,Other spotted fevers,9
A779,0,A779,"Spotted fever, unspecified","Spotted fever, unspecified","Spotted fever, unspecified",9
A78,0,A78,Q fever,Q fever,Q fever,9
A799,0,A799,"Rickettsiosis, unspecified","Rickettsiosis, unspecified","Rickettsiosis, unspecified",9
A804,0,A804,Acute nonparalytic poliomyelitis,Acute nonparalytic poliomyelitis,Acute nonparalytic poliomyelitis,9
A809,0,A809,"Acute poliomyelitis, unspecified","Acute poliomyelitis, unspecified","Acute poliomyelitis, unspecified",9
A811,0,A811,Subacute sclerosing panencephalitis,Subacute sclerosing panencephalitis,Subacute sclerosing panencephalitis,9
A812,0,A812,Progressive multifocal leukoencephalopathy,Progressive multifocal leukoencephalopathy,Progressive multifocal leukoencephalopathy,9
A819,0,A819,"Atypical virus infection of central nervous system, unsp","Atypical virus infection of central nervous system, unspecified","Atypical virus infection of central nervous system, unspecified",9
A86,0,A86,Unspecified viral encephalitis,Unspecified viral encephalitis,Unspecified viral encephalitis,9
A89,0,A89,Unspecified viral infection of central nervous system,Unspecified viral infection of central nervous system,Unspecified viral infection of central nervous system,9
A90,0,A90,Dengue fever [classical dengue],Dengue fever [classical dengue],Dengue fever [classical dengue],9
A91,0,A91,Dengue hemorrhagic fever,Dengue hemorrhagic fever,Dengue hemorrhagic fever,9
A924,0,A924,Rift Valley fever,Rift Valley fever,Rift Valley fever,9
A925,0,A925,Zika virus disease,Zika virus disease,Zika virus disease,9
A928,0,A928,Other specified mosquito-borne viral fevers,Other specified mosquito-borne viral fevers,Other specified mosquito-borne viral fevers,9
A929,0,A929,"Mosquito-borne viral fever, unspecified","Mosquito-borne viral fever, unspecified","Mosquito-borne viral fever, unspecified",9
A94,0,A94,Unspecified arthropod-borne viral fever,Unspecified arthropod-borne viral fever,Unspecified arthropod-borne viral fever,9
A99,0,A99,Unspecified viral hemorrhagic fever,Unspecified viral hemorrhagic fever,Unspecified viral hemorrhagic fever,9
B007,0,B007,Disseminated herpesviral disease,Disseminated herpesviral disease,Disseminated herpesviral disease,9
B009,0,B009,"Herpesviral infection, unspecified","Herpesviral infection, unspecified","Herpesviral infection, unspecified",9
B012,0,B012,Varicella pneumonia,Varicella pneumonia,Varicella pneumonia,9
B019,0,B019,Varicella without complication,Varicella without complication,Varicella without complication,9
B027,0,B027,Disseminated zoster,Disseminated zoster,Disseminated zoster,9
B028,0,B028,Zoster with other complications,Zoster with other complications,Zoster with other complications,9
B029,0,B029,Zoster without complications,Zoster without complications,Zoster without complications,9
B03,0,B03,Smallpox,Smallpox,Smallpox,9
B04,0,B04,Monkeypox,Monkeypox,Monkeypox,9
B059,0,B059,Measles without complication,Measles without complication,Measles without complication,9
B069,0,B069,Rubella without complication,Rubella without complication,Rubella without complication,9
B0802,0,B0802,Orf virus disease,Orf virus disease,Orf virus disease,9
B0803,0,B0803,Pseudocowpox [milker's node],Pseudocowpox [milker's node],Pseudocowpox [milker's node],9
B0804,0,B0804,"Paravaccinia, unspecified","Paravaccinia, unspecified","Paravaccinia, unspecified",9
B0809,0,B0809,Other orthopoxvirus infections,Other orthopoxvirus infections,Other orthopoxvirus infections,9
B081,0,B081,Molluscum contagiosum,Molluscum contagiosum,Molluscum contagiosum,9
B083,0,B083,Erythema infectiosum [fifth disease],Erythema infectiosum [fifth disease],Erythema infectiosum [fifth disease],9
B084,0,B084,Enteroviral vesicular stomatitis with exanthem,Enteroviral vesicular stomatitis with exanthem,Enteroviral vesicular stomatitis with exanthem,9
B085,0,B085,Enteroviral vesicular pharyngitis,Enteroviral vesicular pharyngitis,Enteroviral vesicular pharyngitis,9
B088,0,B088,Oth viral infections with skin and mucous membrane lesions,Other specified viral infections characterized by skin and mucous membrane lesions,Other specified viral infections characterized by skin and mucous membrane lesions,9
B09,0,B09,Unsp viral infection with skin and mucous membrane lesions,Unspecified viral infection characterized by skin and mucous membrane lesions,Unspecified viral infection characterized by skin and mucous membrane lesions,9
B172,0,B172,Acute hepatitis E,Acute hepatitis E,Acute hepatitis E,9
B178,0,B178,Other specified acute viral hepatitis,Other specified acute viral hepatitis,Other specified acute viral hepatitis,9
B179,0,B179,"Acute viral hepatitis, unspecified","Acute viral hepatitis, unspecified","Acute viral hepatitis, unspecified",9
B199,0,B199,Unspecified viral hepatitis without hepatic coma,Unspecified viral hepatitis without hepatic coma,Unspecified viral hepatitis without hepatic coma,9
B20,0,B20,Human immunodeficiency virus [HIV] disease,Human immunodeficiency virus [HIV] disease,Human immunodeficiency virus [HIV] disease,9
B269,0,B269,Mumps without complication,Mumps without complication,Mumps without complication,9
B333,0,B333,"Retrovirus infections, not elsewhere classified","Retrovirus infections, not elsewhere classified","Retrovirus infections, not elsewhere classified",9
B334,0,B334,Hantavirus (cardio)-pulmonary syndrome [HPS] [HCPS],Hantavirus (cardio)-pulmonary syndrome [HPS] [HCPS],Hantavirus (cardio)-pulmonary syndrome [HPS] [HCPS],9
B338,0,B338,Other specified viral diseases,Other specified viral diseases,Other specified viral diseases,9
B375,0,B375,Candidal meningitis,Candidal meningitis,Candidal meningitis,9
B376,0,B376,Candidal endocarditis,Candidal endocarditis,Candidal endocarditis,9
B377,0,B377,Candidal sepsis,Candidal sepsis,Candidal sepsis,9
B379,0,B379,"Candidiasis, unspecified","Candidiasis, unspecified","Candidiasis, unspecified",9
B389,0,B389,"Coccidioidomycosis, unspecified","Coccidioidomycosis, unspecified","Coccidioidomycosis, unspecified",9
B409,0,B409,"Blastomycosis, unspecified","Blastomycosis, unspecified","Blastomycosis, unspecified",9
B429,0,B429,"Sporotrichosis, unspecified","Sporotrichosis, unspecified","Sporotrichosis, unspecified",9
B449,0,B449,"Aspergillosis, unspecified","Aspergillosis, unspecified","Aspergillosis, unspecified",9
B49,0,B49,Unspecified mycosis,Unspecified mycosis,Unspecified mycosis,9
B54,0,B54,Unspecified malaria,Unspecified malaria,Unspecified malaria,9
B575,0,B575,Chagas' disease (chronic) with other organ involvement,Chagas' disease (chronic) with other organ involvement,Chagas' disease (chronic) with other organ involvement,9
B581,0,B581,Toxoplasma hepatitis,Toxoplasma hepatitis,Toxoplasma hepatitis,9
B582,0,B582,Toxoplasma meningoencephalitis,Toxoplasma meningoencephalitis,Toxoplasma meningoencephalitis,9
B583,0,B583,Pulmonary toxoplasmosis,Pulmonary toxoplasmosis,Pulmonary toxoplasmosis,9
B589,0,B589,"Toxoplasmosis, unspecified","Toxoplasmosis, unspecified","Toxoplasmosis, unspecified",9
B59,0,B59,Pneumocystosis,Pneumocystosis,Pneumocystosis,9
B602,0,B602,Naegleriasis,Naegleriasis,Naegleriasis,9
B608,0,B608,Other specified protozoal diseases,Other specified protozoal diseases,Other specified protozoal diseases,9
B64,0,B64,Unspecified protozoal disease,Unspecified protozoal disease,Unspecified protozoal disease,9
B674,0,B674,"Echinococcus granulosus infection, unspecified","Echinococcus granulosus infection, unspecified","Echinococcus granulosus infection, unspecified",9
B675,0,B675,Echinococcus multilocularis infection of liver,Echinococcus multilocularis infection of liver,Echinococcus multilocularis infection of liver,9
B677,0,B677,"Echinococcus multilocularis infection, unspecified","Echinococcus multilocularis infection, unspecified","Echinococcus multilocularis infection, unspecified",9
B678,0,B678,"Echinococcosis, unspecified, of liver","Echinococcosis, unspecified, of liver","Echinococcosis, unspecified, of liver",9
B699,0,B699,"Cysticercosis, unspecified","Cysticercosis, unspecified","Cysticercosis, unspecified",9
B72,0,B72,Dracunculiasis,Dracunculiasis,Dracunculiasis,9
B731,0,B731,Onchocerciasis without eye disease,Onchocerciasis without eye disease,Onchocerciasis without eye disease,9
B75,0,B75,Trichinellosis,Trichinellosis,Trichinellosis,9
B779,0,B779,"Ascariasis, unspecified","Ascariasis, unspecified","Ascariasis, unspecified",9
B79,0,B79,Trichuriasis,Trichuriasis,Trichuriasis,9
B80,0,B80,Enterobiasis,Enterobiasis,Enterobiasis,9
B86,0,B86,Scabies,Scabies,Scabies,9
B879,0,B879,"Myiasis, unspecified","Myiasis, unspecified","Myiasis, unspecified",9
B89,0,B89,Unspecified parasitic disease,Unspecified parasitic disease,Unspecified parasitic disease,9
B91,0,B91,Sequelae of poliomyelitis,Sequelae of poliomyelitis,Sequelae of poliomyelitis,9
B92,0,B92,Sequelae of leprosy,Sequelae of leprosy,Sequelae of leprosy,9
B957,0,B957,Oth staphylococcus as the cause of diseases classd elswhr,Other staphylococcus as the cause of diseases classified elsewhere,Other staphylococcus as the cause of diseases classified elsewhere,9
B958,0,B958,Unsp staphylococcus as the cause of diseases classd elswhr,Unspecified staphylococcus as the cause of diseases classified elsewhere,Unspecified staphylococcus as the cause of diseases classified elsewhere,9
B963,0,B963,Hemophilus influenzae as the cause of diseases classd elswhr,Hemophilus influenzae [H. influenzae] as the cause of diseases classified elsewhere,Hemophilus influenzae [H. influenzae] as the cause of diseases classified elsewhere,9
B964,0,B964,Proteus (mirabilis) (morganii) causing dis classd elswhr,Proteus (mirabilis) (morganii) as the cause of diseases classified elsewhere,Proteus (mirabilis) (morganii) as the cause of diseases classified elsewhere,9
B965,0,B965,Pseudomonas (mallei) causing diseases classd elswhr,Pseudomonas (aeruginosa) (mallei) (pseudomallei) as the cause of diseases classified elsewhere,Pseudomonas (aeruginosa) (mallei) (pseudomallei) as the cause of diseases classified elsewhere,9
B966,0,B966,Bacteroides fragilis as the cause of diseases classd elswhr,Bacteroides fragilis [B. fragilis] as the cause of diseases classified elsewhere,Bacteroides fragilis [B. fragilis] as the cause of diseases classified elsewhere,9
B967,0,B967,Clostridium perfringens causing diseases classd elswhr,Clostridium perfringens [C. perfringens] as the cause of diseases classified elsewhere,Clostridium perfringens [C. perfringens] as the cause of diseases classified elsewhere,9
B974,0,B974,Respiratory syncytial virus causing diseases classd elswhr,Respiratory syncytial virus as the cause of diseases classified elsewhere,Respiratory syncytial virus as the cause of diseases classified elsewhere,9
B975,0,B975,Reovirus as the cause of diseases classified elsewhere,Reovirus as the cause of diseases classified elsewhere,Reovirus as the cause of diseases classified elsewhere,9
B976,0,B976,Parvovirus as the cause of diseases classified elsewhere,Parvovirus as the cause of diseases classified elsewhere,Parvovirus as the cause of diseases classified elsewhere,9
B977,0,B977,Papillomavirus as the cause of diseases classified elsewhere,Papillomavirus as the cause of diseases classified elsewhere,Papillomavirus as the cause of diseases classified elsewhere,9
C01,0,C01,Malignant neoplasm of base of tongue,Malignant neoplasm of base of tongue,Malignant neoplasm of base of tongue,9
C069,0,C069,"Malignant neoplasm of mouth, unspecified","Malignant neoplasm of mouth, unspecified","Malignant neoplasm of mouth, unspecified",9
C07,0,C07,Malignant neoplasm of parotid gland,Malignant neoplasm of parotid gland,Malignant neoplasm of parotid gland,9
C12,0,C12,Malignant neoplasm of pyriform sinus,Malignant neoplasm of pyriform sinus,Malignant neoplasm of pyriform sinus,9
C19,0,C19,Malignant neoplasm of rectosigmoid junction,Malignant neoplasm of rectosigmoid junction,Malignant neoplasm of rectosigmoid junction,9
C20,0,C20,Malignant neoplasm of rectum,Malignant neoplasm of rectum,Malignant neoplasm of rectum,9
C23,0,C23,Malignant neoplasm of gallbladder,Malignant neoplasm of gallbladder,Malignant neoplasm of gallbladder,9
C33,0,C33,Malignant neoplasm of trachea,Malignant neoplasm of trachea,Malignant neoplasm of trachea,9
C342,0,C342,"Malignant neoplasm of middle lobe, bronchus or lung","Malignant neoplasm of middle lobe, bronchus or lung","Malignant neoplasm of middle lobe, bronchus or lung",9
C37,0,C37,Malignant neoplasm of thymus,Malignant neoplasm of thymus,Malignant neoplasm of thymus,9
C434,0,C434,Malignant melanoma of scalp and neck,Malignant melanoma of scalp and neck,Malignant melanoma of scalp and neck,9
C438,0,C438,Malignant melanoma of overlapping sites of skin,Malignant melanoma of overlapping sites of skin,Malignant melanoma of overlapping sites of skin,9
C439,0,C439,"Malignant melanoma of skin, unspecified","Malignant melanoma of skin, unspecified","Malignant melanoma of skin, unspecified",9
C4A4,0,C4A4,Merkel cell carcinoma of scalp and neck,Merkel cell carcinoma of scalp and neck,Merkel cell carcinoma of scalp and neck,9
C4A8,0,C4A8,Merkel cell carcinoma of overlapping sites,Merkel cell carcinoma of overlapping sites,Merkel cell carcinoma of overlapping sites,9
C4A9,0,C4A9,"Merkel cell carcinoma, unspecified","Merkel cell carcinoma, unspecified","Merkel cell carcinoma, unspecified",9
C467,0,C467,Kaposi's sarcoma of other sites,Kaposi's sarcoma of other sites,Kaposi's sarcoma of other sites,9
C469,0,C469,"Kaposi''s sarcoma, unspecified","Kaposi''s sarcoma, unspecified","Kaposi''s sarcoma, unspecified",9
C473,0,C473,Malignant neoplasm of peripheral nerves of thorax,Malignant neoplasm of peripheral nerves of thorax,Malignant neoplasm of peripheral nerves of thorax,9
C474,0,C474,Malignant neoplasm of peripheral nerves of abdomen,Malignant neoplasm of peripheral nerves of abdomen,Malignant neoplasm of peripheral nerves of abdomen,9
C475,0,C475,Malignant neoplasm of peripheral nerves of pelvis,Malignant neoplasm of peripheral nerves of pelvis,Malignant neoplasm of peripheral nerves of pelvis,9
C476,0,C476,"Malignant neoplasm of peripheral nerves of trunk, unsp","Malignant neoplasm of peripheral nerves of trunk, unspecified","Malignant neoplasm of peripheral nerves of trunk, unspecified",9
C478,0,C478,Malig neoplm of ovrlp sites of prph nrv and autonm nrv sys,Malignant neoplasm of overlapping sites of peripheral nerves and autonomic nervous system,Malignant neoplasm of overlapping sites of peripheral nerves and autonomic nervous system,9
C479,0,C479,"Malig neoplasm of prph nerves and autonm nervous sys, unsp","Malignant neoplasm of peripheral nerves and autonomic nervous system, unspecified","Malignant neoplasm of peripheral nerves and autonomic nervous system, unspecified",9
C493,0,C493,Malignant neoplasm of connective and soft tissue of thorax,Malignant neoplasm of connective and soft tissue of thorax,Malignant neoplasm of connective and soft tissue of thorax,9
C494,0,C494,Malignant neoplasm of connective and soft tissue of abdomen,Malignant neoplasm of connective and soft tissue of abdomen,Malignant neoplasm of connective and soft tissue of abdomen,9
C495,0,C495,Malignant neoplasm of connective and soft tissue of pelvis,Malignant neoplasm of connective and soft tissue of pelvis,Malignant neoplasm of connective and soft tissue of pelvis,9
C496,0,C496,"Malignant neoplasm of conn and soft tissue of trunk, unsp","Malignant neoplasm of connective and soft tissue of trunk, unspecified","Malignant neoplasm of connective and soft tissue of trunk, unspecified",9
C498,0,C498,Malignant neoplasm of ovrlp sites of conn and soft tissue,Malignant neoplasm of overlapping sites of connective and soft tissue,Malignant neoplasm of overlapping sites of connective and soft tissue,9
C499,0,C499,"Malignant neoplasm of connective and soft tissue, unsp","Malignant neoplasm of connective and soft tissue, unspecified","Malignant neoplasm of connective and soft tissue, unspecified",9
C52,0,C52,Malignant neoplasm of vagina,Malignant neoplasm of vagina,Malignant neoplasm of vagina,9
C55,0,C55,"Malignant neoplasm of uterus, part unspecified","Malignant neoplasm of uterus, part unspecified","Malignant neoplasm of uterus, part unspecified",9
C573,0,C573,Malignant neoplasm of parametrium,Malignant neoplasm of parametrium,Malignant neoplasm of parametrium,9
C574,0,C574,"Malignant neoplasm of uterine adnexa, unspecified","Malignant neoplasm of uterine adnexa, unspecified","Malignant neoplasm of uterine adnexa, unspecified",9
C577,0,C577,Malignant neoplasm of other specified female genital organs,Malignant neoplasm of other specified female genital organs,Malignant neoplasm of other specified female genital organs,9
C578,0,C578,Malignant neoplasm of ovrlp sites of female genital organs,Malignant neoplasm of overlapping sites of female genital organs,Malignant neoplasm of overlapping sites of female genital organs,9
C579,0,C579,"Malignant neoplasm of female genital organ, unspecified","Malignant neoplasm of female genital organ, unspecified","Malignant neoplasm of female genital organ, unspecified",9
C58,0,C58,Malignant neoplasm of placenta,Malignant neoplasm of placenta,Malignant neoplasm of placenta,9
C61,0,C61,Malignant neoplasm of prostate,Malignant neoplasm of prostate,Malignant neoplasm of prostate,9
C632,0,C632,Malignant neoplasm of scrotum,Malignant neoplasm of scrotum,Malignant neoplasm of scrotum,9
C637,0,C637,Malignant neoplasm of other specified male genital organs,Malignant neoplasm of other specified male genital organs,Malignant neoplasm of other specified male genital organs,9
C638,0,C638,Malignant neoplasm of ovrlp sites of male genital organs,Malignant neoplasm of overlapping sites of male genital organs,Malignant neoplasm of overlapping sites of male genital organs,9
C639,0,C639,"Malignant neoplasm of male genital organ, unspecified","Malignant neoplasm of male genital organ, unspecified","Malignant neoplasm of male genital organ, unspecified",9
C729,0,C729,"Malignant neoplasm of central nervous system, unspecified","Malignant neoplasm of central nervous system, unspecified","Malignant neoplasm of central nervous system, unspecified",9
C73,0,C73,Malignant neoplasm of thyroid gland,Malignant neoplasm of thyroid gland,Malignant neoplasm of thyroid gland,9
C7A1,0,C7A1,Malignant poorly differentiated neuroendocrine tumors,Malignant poorly differentiated neuroendocrine tumors,Malignant poorly differentiated neuroendocrine tumors,9
C7A8,0,C7A8,Other malignant neuroendocrine tumors,Other malignant neuroendocrine tumors,Other malignant neuroendocrine tumors,9
C7B1,0,C7B1,Secondary Merkel cell carcinoma,Secondary Merkel cell carcinoma,Secondary Merkel cell carcinoma,9
C7B8,0,C7B8,Other secondary neuroendocrine tumors,Other secondary neuroendocrine tumors,Other secondary neuroendocrine tumors,9
C768,0,C768,Malignant neoplasm of other specified ill-defined sites,Malignant neoplasm of other specified ill-defined sites,Malignant neoplasm of other specified ill-defined sites,9
C781,0,C781,Secondary malignant neoplasm of mediastinum,Secondary malignant neoplasm of mediastinum,Secondary malignant neoplasm of mediastinum,9
C782,0,C782,Secondary malignant neoplasm of pleura,Secondary malignant neoplasm of pleura,Secondary malignant neoplasm of pleura,9
C784,0,C784,Secondary malignant neoplasm of small intestine,Secondary malignant neoplasm of small intestine,Secondary malignant neoplasm of small intestine,9
C785,0,C785,Secondary malignant neoplasm of large intestine and rectum,Secondary malignant neoplasm of large intestine and rectum,Secondary malignant neoplasm of large intestine and rectum,9
D611,0,D611,Drug-induced aplastic anemia,Drug-induced aplastic anemia,Drug-induced aplastic anemia,9
C786,0,C786,Secondary malignant neoplasm of retroperiton and peritoneum,Secondary malignant neoplasm of retroperitoneum and peritoneum,Secondary malignant neoplasm of retroperitoneum and peritoneum,9
C787,0,C787,Secondary malig neoplasm of liver and intrahepatic bile duct,Secondary malignant neoplasm of liver and intrahepatic bile duct,Secondary malignant neoplasm of liver and intrahepatic bile duct,9
C792,0,C792,Secondary malignant neoplasm of skin,Secondary malignant neoplasm of skin,Secondary malignant neoplasm of skin,9
C799,0,C799,Secondary malignant neoplasm of unspecified site,Secondary malignant neoplasm of unspecified site,Secondary malignant neoplasm of unspecified site,9
C946,0,C946,"Myelodysplastic disease, not classified","Myelodysplastic disease, not classified","Myelodysplastic disease, not classified",9
C964,0,C964,Sarcoma of dendritic cells (accessory cells),Sarcoma of dendritic cells (accessory cells),Sarcoma of dendritic cells (accessory cells),9
C965,0,C965,Multifocal and unisystemic Langerhans-cell histiocytosis,Multifocal and unisystemic Langerhans-cell histiocytosis,Multifocal and unisystemic Langerhans-cell histiocytosis,9
C966,0,C966,Unifocal Langerhans-cell histiocytosis,Unifocal Langerhans-cell histiocytosis,Unifocal Langerhans-cell histiocytosis,9
C96A,0,C96A,Histiocytic sarcoma,Histiocytic sarcoma,Histiocytic sarcoma,9
C96Z,0,C96Z,"Oth malig neoplm of lymphoid, hematpoetc and related tissue","Other specified malignant neoplasms of lymphoid, hematopoietic and related tissue","Other specified malignant neoplasms of lymphoid, hematopoietic and related tissue",9
C969,0,C969,"Malig neoplm of lymphoid, hematpoetc and rel tissue, unsp","Malignant neoplasm of lymphoid, hematopoietic and related tissue, unspecified","Malignant neoplasm of lymphoid, hematopoietic and related tissue, unspecified",9
D001,0,D001,Carcinoma in situ of esophagus,Carcinoma in situ of esophagus,Carcinoma in situ of esophagus,9
D002,0,D002,Carcinoma in situ of stomach,Carcinoma in situ of stomach,Carcinoma in situ of stomach,9
D015,0,D015,"Carcinoma in situ of liver, gallbladder and bile ducts","Carcinoma in situ of liver, gallbladder and bile ducts","Carcinoma in situ of liver, gallbladder and bile ducts",9
D017,0,D017,Carcinoma in situ of other specified digestive organs,Carcinoma in situ of other specified digestive organs,Carcinoma in situ of other specified digestive organs,9
D019,0,D019,"Carcinoma in situ of digestive organ, unspecified","Carcinoma in situ of digestive organ, unspecified","Carcinoma in situ of digestive organ, unspecified",9
D023,0,D023,Carcinoma in situ of other parts of respiratory system,Carcinoma in situ of other parts of respiratory system,Carcinoma in situ of other parts of respiratory system,9
D024,0,D024,"Carcinoma in situ of respiratory system, unspecified","Carcinoma in situ of respiratory system, unspecified","Carcinoma in situ of respiratory system, unspecified",9
D034,0,D034,Melanoma in situ of scalp and neck,Melanoma in situ of scalp and neck,Melanoma in situ of scalp and neck,9
D038,0,D038,Melanoma in situ of other sites,Melanoma in situ of other sites,Melanoma in situ of other sites,9
D039,0,D039,"Melanoma in situ, unspecified","Melanoma in situ, unspecified","Melanoma in situ, unspecified",9
D044,0,D044,Carcinoma in situ of skin of scalp and neck,Carcinoma in situ of skin of scalp and neck,Carcinoma in situ of skin of scalp and neck,9
D045,0,D045,Carcinoma in situ of skin of trunk,Carcinoma in situ of skin of trunk,Carcinoma in situ of skin of trunk,9
D048,0,D048,Carcinoma in situ of skin of other sites,Carcinoma in situ of skin of other sites,Carcinoma in situ of skin of other sites,9
D049,0,D049,"Carcinoma in situ of skin, unspecified","Carcinoma in situ of skin, unspecified","Carcinoma in situ of skin, unspecified",9
D074,0,D074,Carcinoma in situ of penis,Carcinoma in situ of penis,Carcinoma in situ of penis,9
D075,0,D075,Carcinoma in situ of prostate,Carcinoma in situ of prostate,Carcinoma in situ of prostate,9
D093,0,D093,Carcinoma in situ of thyroid and other endocrine glands,Carcinoma in situ of thyroid and other endocrine glands,Carcinoma in situ of thyroid and other endocrine glands,9
D098,0,D098,Carcinoma in situ of other specified sites,Carcinoma in situ of other specified sites,Carcinoma in situ of other specified sites,9
D099,0,D099,"Carcinoma in situ, unspecified","Carcinoma in situ, unspecified","Carcinoma in situ, unspecified",9
D104,0,D104,Benign neoplasm of tonsil,Benign neoplasm of tonsil,Benign neoplasm of tonsil,9
D105,0,D105,Benign neoplasm of other parts of oropharynx,Benign neoplasm of other parts of oropharynx,Benign neoplasm of other parts of oropharynx,9
D106,0,D106,Benign neoplasm of nasopharynx,Benign neoplasm of nasopharynx,Benign neoplasm of nasopharynx,9
D107,0,D107,Benign neoplasm of hypopharynx,Benign neoplasm of hypopharynx,Benign neoplasm of hypopharynx,9
D109,0,D109,"Benign neoplasm of pharynx, unspecified","Benign neoplasm of pharynx, unspecified","Benign neoplasm of pharynx, unspecified",9
D134,0,D134,Benign neoplasm of liver,Benign neoplasm of liver,Benign neoplasm of liver,9
D135,0,D135,Benign neoplasm of extrahepatic bile ducts,Benign neoplasm of extrahepatic bile ducts,Benign neoplasm of extrahepatic bile ducts,9
D136,0,D136,Benign neoplasm of pancreas,Benign neoplasm of pancreas,Benign neoplasm of pancreas,9
D137,0,D137,Benign neoplasm of endocrine pancreas,Benign neoplasm of endocrine pancreas,Benign neoplasm of endocrine pancreas,9
D139,0,D139,Benign neoplasm of ill-defined sites within the dgstv sys,Benign neoplasm of ill-defined sites within the digestive system,Benign neoplasm of ill-defined sites within the digestive system,9
D144,0,D144,"Benign neoplasm of respiratory system, unspecified","Benign neoplasm of respiratory system, unspecified","Benign neoplasm of respiratory system, unspecified",9
D164,0,D164,Benign neoplasm of bones of skull and face,Benign neoplasm of bones of skull and face,Benign neoplasm of bones of skull and face,9
D165,0,D165,Benign neoplasm of lower jaw bone,Benign neoplasm of lower jaw bone,Benign neoplasm of lower jaw bone,9
D166,0,D166,Benign neoplasm of vertebral column,Benign neoplasm of vertebral column,Benign neoplasm of vertebral column,9
D167,0,D167,"Benign neoplasm of ribs, sternum and clavicle","Benign neoplasm of ribs, sternum and clavicle","Benign neoplasm of ribs, sternum and clavicle",9
D168,0,D168,"Benign neoplasm of pelvic bones, sacrum and coccyx","Benign neoplasm of pelvic bones, sacrum and coccyx","Benign neoplasm of pelvic bones, sacrum and coccyx",9
D169,0,D169,"Benign neoplasm of bone and articular cartilage, unspecified","Benign neoplasm of bone and articular cartilage, unspecified","Benign neoplasm of bone and articular cartilage, unspecified",9
D174,0,D174,Benign lipomatous neoplasm of intrathoracic organs,Benign lipomatous neoplasm of intrathoracic organs,Benign lipomatous neoplasm of intrathoracic organs,9
D175,0,D175,Benign lipomatous neoplasm of intra-abdominal organs,Benign lipomatous neoplasm of intra-abdominal organs,Benign lipomatous neoplasm of intra-abdominal organs,9
D176,0,D176,Benign lipomatous neoplasm of spermatic cord,Benign lipomatous neoplasm of spermatic cord,Benign lipomatous neoplasm of spermatic cord,9
D179,0,D179,"Benign lipomatous neoplasm, unspecified","Benign lipomatous neoplasm, unspecified","Benign lipomatous neoplasm, unspecified",9
D181,0,D181,"Lymphangioma, any site","Lymphangioma, any site","Lymphangioma, any site",9
D213,0,D213,Benign neoplasm of connective and oth soft tissue of thorax,Benign neoplasm of connective and other soft tissue of thorax,Benign neoplasm of connective and other soft tissue of thorax,9
D214,0,D214,Benign neoplasm of connective and oth soft tissue of abdomen,Benign neoplasm of connective and other soft tissue of abdomen,Benign neoplasm of connective and other soft tissue of abdomen,9
D215,0,D215,Benign neoplasm of connective and oth soft tissue of pelvis,Benign neoplasm of connective and other soft tissue of pelvis,Benign neoplasm of connective and other soft tissue of pelvis,9
D216,0,D216,"Benign neoplasm of connctv/soft tiss of trunk, unsp","Benign neoplasm of connective and other soft tissue of trunk, unspecified","Benign neoplasm of connective and other soft tissue of trunk, unspecified",9
D219,0,D219,"Benign neoplasm of connective and other soft tissue, unsp","Benign neoplasm of connective and other soft tissue, unspecified","Benign neoplasm of connective and other soft tissue, unspecified",9
D224,0,D224,Melanocytic nevi of scalp and neck,Melanocytic nevi of scalp and neck,Melanocytic nevi of scalp and neck,9
D225,0,D225,Melanocytic nevi of trunk,Melanocytic nevi of trunk,Melanocytic nevi of trunk,9
D229,0,D229,"Melanocytic nevi, unspecified","Melanocytic nevi, unspecified","Melanocytic nevi, unspecified",9
D234,0,D234,Other benign neoplasm of skin of scalp and neck,Other benign neoplasm of skin of scalp and neck,Other benign neoplasm of skin of scalp and neck,9
D235,0,D235,Other benign neoplasm of skin of trunk,Other benign neoplasm of skin of trunk,Other benign neoplasm of skin of trunk,9
D239,0,D239,"Other benign neoplasm of skin, unspecified","Other benign neoplasm of skin, unspecified","Other benign neoplasm of skin, unspecified",9
D294,0,D294,Benign neoplasm of scrotum,Benign neoplasm of scrotum,Benign neoplasm of scrotum,9
D298,0,D298,Benign neoplasm of other specified male genital organs,Benign neoplasm of other specified male genital organs,Benign neoplasm of other specified male genital organs,9
D299,0,D299,"Benign neoplasm of male genital organ, unspecified","Benign neoplasm of male genital organ, unspecified","Benign neoplasm of male genital organ, unspecified",9
D303,0,D303,Benign neoplasm of bladder,Benign neoplasm of bladder,Benign neoplasm of bladder,9
D304,0,D304,Benign neoplasm of urethra,Benign neoplasm of urethra,Benign neoplasm of urethra,9
D308,0,D308,Benign neoplasm of other specified urinary organs,Benign neoplasm of other specified urinary organs,Benign neoplasm of other specified urinary organs,9
D309,0,D309,"Benign neoplasm of urinary organ, unspecified","Benign neoplasm of urinary organ, unspecified","Benign neoplasm of urinary organ, unspecified",9
D34,0,D34,Benign neoplasm of thyroid gland,Benign neoplasm of thyroid gland,Benign neoplasm of thyroid gland,9
D351,0,D351,Benign neoplasm of parathyroid gland,Benign neoplasm of parathyroid gland,Benign neoplasm of parathyroid gland,9
D352,0,D352,Benign neoplasm of pituitary gland,Benign neoplasm of pituitary gland,Benign neoplasm of pituitary gland,9
D353,0,D353,Benign neoplasm of craniopharyngeal duct,Benign neoplasm of craniopharyngeal duct,Benign neoplasm of craniopharyngeal duct,9
D354,0,D354,Benign neoplasm of pineal gland,Benign neoplasm of pineal gland,Benign neoplasm of pineal gland,9
D355,0,D355,Benign neoplasm of carotid body,Benign neoplasm of carotid body,Benign neoplasm of carotid body,9
D356,0,D356,Benign neoplasm of aortic body and other paraganglia,Benign neoplasm of aortic body and other paraganglia,Benign neoplasm of aortic body and other paraganglia,9
D357,0,D357,Benign neoplasm of other specified endocrine glands,Benign neoplasm of other specified endocrine glands,Benign neoplasm of other specified endocrine glands,9
D359,0,D359,"Benign neoplasm of endocrine gland, unspecified","Benign neoplasm of endocrine gland, unspecified","Benign neoplasm of endocrine gland, unspecified",9
D367,0,D367,Benign neoplasm of other specified sites,Benign neoplasm of other specified sites,Benign neoplasm of other specified sites,9
D369,0,D369,"Benign neoplasm, unspecified site","Benign neoplasm, unspecified site","Benign neoplasm, unspecified site",9
D3A8,0,D3A8,Other benign neuroendocrine tumors,Other benign neuroendocrine tumors,Other benign neuroendocrine tumors,9
D3704,0,D3704,Neoplasm of uncertain behavior of the minor salivary glands,Neoplasm of uncertain behavior of the minor salivary glands,Neoplasm of uncertain behavior of the minor salivary glands,9
D3705,0,D3705,Neoplasm of uncertain behavior of pharynx,Neoplasm of uncertain behavior of pharynx,Neoplasm of uncertain behavior of pharynx,9
D3709,0,D3709,Neoplasm of uncertain behavior of sites of the oral cavity,Neoplasm of uncertain behavior of other specified sites of the oral cavity,Neoplasm of uncertain behavior of other specified sites of the oral cavity,9
D371,0,D371,Neoplasm of uncertain behavior of stomach,Neoplasm of uncertain behavior of stomach,Neoplasm of uncertain behavior of stomach,9
D372,0,D372,Neoplasm of uncertain behavior of small intestine,Neoplasm of uncertain behavior of small intestine,Neoplasm of uncertain behavior of small intestine,9
D373,0,D373,Neoplasm of uncertain behavior of appendix,Neoplasm of uncertain behavior of appendix,Neoplasm of uncertain behavior of appendix,9
D374,0,D374,Neoplasm of uncertain behavior of colon,Neoplasm of uncertain behavior of colon,Neoplasm of uncertain behavior of colon,9
D375,0,D375,Neoplasm of uncertain behavior of rectum,Neoplasm of uncertain behavior of rectum,Neoplasm of uncertain behavior of rectum,9
D376,0,D376,"Neoplasm of uncertain behavior of liver, GB & bile duct","Neoplasm of uncertain behavior of liver, gallbladder and bile ducts","Neoplasm of uncertain behavior of liver, gallbladder and bile ducts",9
D378,0,D378,Neoplasm of uncertain behavior of oth digestive organs,Neoplasm of uncertain behavior of other specified digestive organs,Neoplasm of uncertain behavior of other specified digestive organs,9
D379,0,D379,"Neoplasm of uncertain behavior of digestive organ, unsp","Neoplasm of uncertain behavior of digestive organ, unspecified","Neoplasm of uncertain behavior of digestive organ, unspecified",9
D392,0,D392,Neoplasm of uncertain behavior of placenta,Neoplasm of uncertain behavior of placenta,Neoplasm of uncertain behavior of placenta,9
D398,0,D398,Neoplasm of uncertain behavior of oth female genital organs,Neoplasm of uncertain behavior of other specified female genital organs,Neoplasm of uncertain behavior of other specified female genital organs,9
D399,0,D399,"Neoplasm of uncertain behavior of female genital organ, unsp","Neoplasm of uncertain behavior of female genital organ, unspecified","Neoplasm of uncertain behavior of female genital organ, unspecified",9
D408,0,D408,Neoplasm of uncertain behavior of oth male genital organs,Neoplasm of uncertain behavior of other specified male genital organs,Neoplasm of uncertain behavior of other specified male genital organs,9
D409,0,D409,"Neoplasm of uncertain behavior of male genital organ, unsp","Neoplasm of uncertain behavior of male genital organ, unspecified","Neoplasm of uncertain behavior of male genital organ, unspecified",9
D413,0,D413,Neoplasm of uncertain behavior of urethra,Neoplasm of uncertain behavior of urethra,Neoplasm of uncertain behavior of urethra,9
D414,0,D414,Neoplasm of uncertain behavior of bladder,Neoplasm of uncertain behavior of bladder,Neoplasm of uncertain behavior of bladder,9
D418,0,D418,Neoplasm of uncertain behavior of oth urinary organs,Neoplasm of uncertain behavior of other specified urinary organs,Neoplasm of uncertain behavior of other specified urinary organs,9
D419,0,D419,Neoplasm of uncertain behavior of unspecified urinary organ,Neoplasm of uncertain behavior of unspecified urinary organ,Neoplasm of uncertain behavior of unspecified urinary organ,9
D442,0,D442,Neoplasm of uncertain behavior of parathyroid gland,Neoplasm of uncertain behavior of parathyroid gland,Neoplasm of uncertain behavior of parathyroid gland,9
D443,0,D443,Neoplasm of uncertain behavior of pituitary gland,Neoplasm of uncertain behavior of pituitary gland,Neoplasm of uncertain behavior of pituitary gland,9
D444,0,D444,Neoplasm of uncertain behavior of craniopharyngeal duct,Neoplasm of uncertain behavior of craniopharyngeal duct,Neoplasm of uncertain behavior of craniopharyngeal duct,9
D445,0,D445,Neoplasm of uncertain behavior of pineal gland,Neoplasm of uncertain behavior of pineal gland,Neoplasm of uncertain behavior of pineal gland,9
D446,0,D446,Neoplasm of uncertain behavior of carotid body,Neoplasm of uncertain behavior of carotid body,Neoplasm of uncertain behavior of carotid body,9
D447,0,D447,Neoplasm of uncrt behav of aortic body and oth paraganglia,Neoplasm of uncertain behavior of aortic body and other paraganglia,Neoplasm of uncertain behavior of aortic body and other paraganglia,9
D449,0,D449,Neoplasm of uncertain behavior of unsp endocrine gland,Neoplasm of uncertain behavior of unspecified endocrine gland,Neoplasm of uncertain behavior of unspecified endocrine gland,9
D45,0,D45,Polycythemia vera,Polycythemia vera,Polycythemia vera,9
D46A,0,D46A,Refractory cytopenia with multilineage dysplasia,Refractory cytopenia with multilineage dysplasia,Refractory cytopenia with multilineage dysplasia,9
D46B,0,D46B,Refract cytopenia w multilin dysplasia and ring sideroblasts,Refractory cytopenia with multilineage dysplasia and ring sideroblasts,Refractory cytopenia with multilineage dysplasia and ring sideroblasts,9
D46C,0,D46C,Myelodysplastic syndrome w isolated del(5q) chromsoml abnlt,Myelodysplastic syndrome with isolated del(5q) chromosomal abnormality,Myelodysplastic syndrome with isolated del(5q) chromosomal abnormality,9
D464,0,D464,"Refractory anemia, unspecified","Refractory anemia, unspecified","Refractory anemia, unspecified",9
D46Z,0,D46Z,Other myelodysplastic syndromes,Other myelodysplastic syndromes,Other myelodysplastic syndromes,9
D469,0,D469,"Myelodysplastic syndrome, unspecified","Myelodysplastic syndrome, unspecified","Myelodysplastic syndrome, unspecified",9
D471,0,D471,Chronic myeloproliferative disease,Chronic myeloproliferative disease,Chronic myeloproliferative disease,9
D472,0,D472,Monoclonal gammopathy,Monoclonal gammopathy,Monoclonal gammopathy,9
D473,0,D473,Essential (hemorrhagic) thrombocythemia,Essential (hemorrhagic) thrombocythemia,Essential (hemorrhagic) thrombocythemia,9
D474,0,D474,Osteomyelofibrosis,Osteomyelofibrosis,Osteomyelofibrosis,9
D479,0,D479,"Neoplm of uncrt behav of lymphoid,hematpoetc & rel tiss,unsp","Neoplasm of uncertain behavior of lymphoid, hematopoietic and related tissue, unspecified","Neoplasm of uncertain behavior of lymphoid, hematopoietic and related tissue, unspecified",9
D487,0,D487,Neoplasm of uncertain behavior of other specified sites,Neoplasm of uncertain behavior of other specified sites,Neoplasm of uncertain behavior of other specified sites,9
D489,0,D489,"Neoplasm of uncertain behavior, unspecified","Neoplasm of uncertain behavior, unspecified","Neoplasm of uncertain behavior, unspecified",9
D4959,0,D4959,Neoplasm of unspecified behavior of other GU organ,Neoplasm of unspecified behavior of other genitourinary organ,Neoplasm of unspecified behavior of other genitourinary organ,9
D496,0,D496,Neoplasm of unspecified behavior of brain,Neoplasm of unspecified behavior of brain,Neoplasm of unspecified behavior of brain,9
D497,0,D497,Neoplm of unsp behav of endo glands and oth prt nervous sys,Neoplasm of unspecified behavior of endocrine glands and other parts of nervous system,Neoplasm of unspecified behavior of endocrine glands and other parts of nervous system,9
D499,0,D499,Neoplasm of unspecified behavior of unspecified site,Neoplasm of unspecified behavior of unspecified site,Neoplasm of unspecified behavior of unspecified site,9
D571,0,D571,Sickle-cell disease without crisis,Sickle-cell disease without crisis,Sickle-cell disease without crisis,9
D573,0,D573,Sickle-cell trait,Sickle-cell trait,Sickle-cell trait,9
D612,0,D612,Aplastic anemia due to other external agents,Aplastic anemia due to other external agents,Aplastic anemia due to other external agents,9
D613,0,D613,Idiopathic aplastic anemia,Idiopathic aplastic anemia,Idiopathic aplastic anemia,9
D6182,0,D6182,Myelophthisis,Myelophthisis,Myelophthisis,9
D6189,0,D6189,Oth aplastic anemias and other bone marrow failure syndromes,Other specified aplastic anemias and other bone marrow failure syndromes,Other specified aplastic anemias and other bone marrow failure syndromes,9
D619,0,D619,"Aplastic anemia, unspecified","Aplastic anemia, unspecified","Aplastic anemia, unspecified",9
D62,0,D62,Acute posthemorrhagic anemia,Acute posthemorrhagic anemia,Acute posthemorrhagic anemia,9
D649,0,D649,"Anemia, unspecified","Anemia, unspecified","Anemia, unspecified",9
D65,0,D65,Disseminated intravascular coagulation,Disseminated intravascular coagulation [defibrination syndrome],Disseminated intravascular coagulation [defibrination syndrome],9
D66,0,D66,Hereditary factor VIII deficiency,Hereditary factor VIII deficiency,Hereditary factor VIII deficiency,9
D67,0,D67,Hereditary factor IX deficiency,Hereditary factor IX deficiency,Hereditary factor IX deficiency,9
D6832,0,D6832,Hemorrhagic disord d/t extrinsic circulating anticoagulants,Hemorrhagic disorder due to extrinsic circulating anticoagulants,Hemorrhagic disorder due to extrinsic circulating anticoagulants,9
D684,0,D684,Acquired coagulation factor deficiency,Acquired coagulation factor deficiency,Acquired coagulation factor deficiency,9
D688,0,D688,Other specified coagulation defects,Other specified coagulation defects,Other specified coagulation defects,9
D689,0,D689,"Coagulation defect, unspecified","Coagulation defect, unspecified","Coagulation defect, unspecified",9
D696,0,D696,"Thrombocytopenia, unspecified","Thrombocytopenia, unspecified","Thrombocytopenia, unspecified",9
D698,0,D698,Other specified hemorrhagic conditions,Other specified hemorrhagic conditions,Other specified hemorrhagic conditions,9
D699,0,D699,"Hemorrhagic condition, unspecified","Hemorrhagic condition, unspecified","Hemorrhagic condition, unspecified",9
D71,0,D71,Functional disorders of polymorphonuclear neutrophils,Functional disorders of polymorphonuclear neutrophils,Functional disorders of polymorphonuclear neutrophils,9
D7289,0,D7289,Other specified disorders of white blood cells,Other specified disorders of white blood cells,Other specified disorders of white blood cells,9
D729,0,D729,"Disorder of white blood cells, unspecified","Disorder of white blood cells, unspecified","Disorder of white blood cells, unspecified",9
D739,0,D739,"Disease of spleen, unspecified","Disease of spleen, unspecified","Disease of spleen, unspecified",9
D759,0,D759,"Disease of blood and blood-forming organs, unspecified","Disease of blood and blood-forming organs, unspecified","Disease of blood and blood-forming organs, unspecified",9
D77,0,D77,Oth disord of bld/bld-frm organs in diseases classd elswhr,Other disorders of blood and blood-forming organs in diseases classified elsewhere,Other disorders of blood and blood-forming organs in diseases classified elsewhere,9
D8189,0,D8189,Other combined immunodeficiencies,Other combined immunodeficiencies,Other combined immunodeficiencies,9
D819,0,D819,"Combined immunodeficiency, unspecified","Combined immunodeficiency, unspecified","Combined immunodeficiency, unspecified",9
D869,0,D869,"Sarcoidosis, unspecified","Sarcoidosis, unspecified","Sarcoidosis, unspecified",9
D8982,0,D8982,Autoimmune lymphoproliferative syndrome [ALPS],Autoimmune lymphoproliferative syndrome [ALPS],Autoimmune lymphoproliferative syndrome [ALPS],9
D8989,0,D8989,"Oth disrd involving the immune mechanism, NEC","Other specified disorders involving the immune mechanism, not elsewhere classified","Other specified disorders involving the immune mechanism, not elsewhere classified",9
D899,0,D899,"Disorder involving the immune mechanism, unspecified","Disorder involving the immune mechanism, unspecified","Disorder involving the immune mechanism, unspecified",9
E02,0,E02,Subclinical iodine-deficiency hypothyroidism,Subclinical iodine-deficiency hypothyroidism,Subclinical iodine-deficiency hypothyroidism,9
E079,0,E079,"Disorder of thyroid, unspecified","Disorder of thyroid, unspecified","Disorder of thyroid, unspecified",9
E0836,0,E0836,Diabetes due to underlying condition w diabetic cataract,Diabetes mellitus due to underlying condition with diabetic cataract,Diabetes mellitus due to underlying condition with diabetic cataract,9
E0839,0,E0839,Diabetes due to undrl condition w oth diabetic opth comp,Diabetes mellitus due to underlying condition with other diabetic ophthalmic complication,Diabetes mellitus due to underlying condition with other diabetic ophthalmic complication,9
E0865,0,E0865,Diabetes due to underlying condition w hyperglycemia,Diabetes mellitus due to underlying condition with hyperglycemia,Diabetes mellitus due to underlying condition with hyperglycemia,9
E0869,0,E0869,Diabetes due to underlying condition w oth complication,Diabetes mellitus due to underlying condition with other specified complication,Diabetes mellitus due to underlying condition with other specified complication,9
E088,0,E088,Diabetes due to underlying condition w unsp complications,Diabetes mellitus due to underlying condition with unspecified complications,Diabetes mellitus due to underlying condition with unspecified complications,9
E089,0,E089,Diabetes due to underlying condition w/o complications,Diabetes mellitus due to underlying condition without complications,Diabetes mellitus due to underlying condition without complications,9
E0936,0,E0936,Drug/chem diabetes mellitus w diabetic cataract,Drug or chemical induced diabetes mellitus with diabetic cataract,Drug or chemical induced diabetes mellitus with diabetic cataract,9
E0939,0,E0939,Drug/chem diabetes w oth diabetic ophthalmic complication,Drug or chemical induced diabetes mellitus with other diabetic ophthalmic complication,Drug or chemical induced diabetes mellitus with other diabetic ophthalmic complication,9
E0965,0,E0965,Drug or chemical induced diabetes mellitus w hyperglycemia,Drug or chemical induced diabetes mellitus with hyperglycemia,Drug or chemical induced diabetes mellitus with hyperglycemia,9
E0969,0,E0969,Drug/chem diabetes mellitus w oth complication,Drug or chemical induced diabetes mellitus with other specified complication,Drug or chemical induced diabetes mellitus with other specified complication,9
F308,0,F308,Other manic episodes,Other manic episodes,Other manic episodes,9
E098,0,E098,Drug/chem diabetes mellitus w unsp complications,Drug or chemical induced diabetes mellitus with unspecified complications,Drug or chemical induced diabetes mellitus with unspecified complications,9
E099,0,E099,Drug or chemical induced diabetes mellitus w/o complications,Drug or chemical induced diabetes mellitus without complications,Drug or chemical induced diabetes mellitus without complications,9
E1036,0,E1036,Type 1 diabetes mellitus with diabetic cataract,Type 1 diabetes mellitus with diabetic cataract,Type 1 diabetes mellitus with diabetic cataract,9
E1039,0,E1039,Type 1 diabetes w oth diabetic ophthalmic complication,Type 1 diabetes mellitus with other diabetic ophthalmic complication,Type 1 diabetes mellitus with other diabetic ophthalmic complication,9
E1065,0,E1065,Type 1 diabetes mellitus with hyperglycemia,Type 1 diabetes mellitus with hyperglycemia,Type 1 diabetes mellitus with hyperglycemia,9
E1069,0,E1069,Type 1 diabetes mellitus with other specified complication,Type 1 diabetes mellitus with other specified complication,Type 1 diabetes mellitus with other specified complication,9
E108,0,E108,Type 1 diabetes mellitus with unspecified complications,Type 1 diabetes mellitus with unspecified complications,Type 1 diabetes mellitus with unspecified complications,9
E109,0,E109,Type 1 diabetes mellitus without complications,Type 1 diabetes mellitus without complications,Type 1 diabetes mellitus without complications,9
E1136,0,E1136,Type 2 diabetes mellitus with diabetic cataract,Type 2 diabetes mellitus with diabetic cataract,Type 2 diabetes mellitus with diabetic cataract,9
E1139,0,E1139,Type 2 diabetes w oth diabetic ophthalmic complication,Type 2 diabetes mellitus with other diabetic ophthalmic complication,Type 2 diabetes mellitus with other diabetic ophthalmic complication,9
E1165,0,E1165,Type 2 diabetes mellitus with hyperglycemia,Type 2 diabetes mellitus with hyperglycemia,Type 2 diabetes mellitus with hyperglycemia,9
E1169,0,E1169,Type 2 diabetes mellitus with other specified complication,Type 2 diabetes mellitus with other specified complication,Type 2 diabetes mellitus with other specified complication,9
E118,0,E118,Type 2 diabetes mellitus with unspecified complications,Type 2 diabetes mellitus with unspecified complications,Type 2 diabetes mellitus with unspecified complications,9
E119,0,E119,Type 2 diabetes mellitus without complications,Type 2 diabetes mellitus without complications,Type 2 diabetes mellitus without complications,9
E1336,0,E1336,Other specified diabetes mellitus with diabetic cataract,Other specified diabetes mellitus with diabetic cataract,Other specified diabetes mellitus with diabetic cataract,9
E1339,0,E1339,Oth diabetes mellitus w oth diabetic ophthalmic complication,Other specified diabetes mellitus with other diabetic ophthalmic complication,Other specified diabetes mellitus with other diabetic ophthalmic complication,9
E1365,0,E1365,Other specified diabetes mellitus with hyperglycemia,Other specified diabetes mellitus with hyperglycemia,Other specified diabetes mellitus with hyperglycemia,9
E1369,0,E1369,Oth diabetes mellitus with other specified complication,Other specified diabetes mellitus with other specified complication,Other specified diabetes mellitus with other specified complication,9
E138,0,E138,Oth diabetes mellitus with unspecified complications,Other specified diabetes mellitus with unspecified complications,Other specified diabetes mellitus with unspecified complications,9
E139,0,E139,Other specified diabetes mellitus without complications,Other specified diabetes mellitus without complications,Other specified diabetes mellitus without complications,9
E15,0,E15,Nondiabetic hypoglycemic coma,Nondiabetic hypoglycemic coma,Nondiabetic hypoglycemic coma,9
E261,0,E261,Secondary hyperaldosteronism,Secondary hyperaldosteronism,Secondary hyperaldosteronism,9
E269,0,E269,"Hyperaldosteronism, unspecified","Hyperaldosteronism, unspecified","Hyperaldosteronism, unspecified",9
E275,0,E275,Adrenomedullary hyperfunction,Adrenomedullary hyperfunction,Adrenomedullary hyperfunction,9
E278,0,E278,Other specified disorders of adrenal gland,Other specified disorders of adrenal gland,Other specified disorders of adrenal gland,9
E279,0,E279,"Disorder of adrenal gland, unspecified","Disorder of adrenal gland, unspecified","Disorder of adrenal gland, unspecified",9
E2839,0,E2839,Other primary ovarian failure,Other primary ovarian failure,Other primary ovarian failure,9
E288,0,E288,Other ovarian dysfunction,Other ovarian dysfunction,Other ovarian dysfunction,9
E289,0,E289,"Ovarian dysfunction, unspecified","Ovarian dysfunction, unspecified","Ovarian dysfunction, unspecified",9
E318,0,E318,Other polyglandular dysfunction,Other polyglandular dysfunction,Other polyglandular dysfunction,9
E319,0,E319,"Polyglandular dysfunction, unspecified","Polyglandular dysfunction, unspecified","Polyglandular dysfunction, unspecified",9
E348,0,E348,Other specified endocrine disorders,Other specified endocrine disorders,Other specified endocrine disorders,9
E349,0,E349,"Endocrine disorder, unspecified","Endocrine disorder, unspecified","Endocrine disorder, unspecified",9
E35,0,E35,Disorders of endocrine glands in diseases classd elswhr,Disorders of endocrine glands in diseases classified elsewhere,Disorders of endocrine glands in diseases classified elsewhere,9
E368,0,E368,Other intraoperative complications of endocrine system,Other intraoperative complications of endocrine system,Other intraoperative complications of endocrine system,9
E40,0,E40,Kwashiorkor,Kwashiorkor,Kwashiorkor,9
E41,0,E41,Nutritional marasmus,Nutritional marasmus,Nutritional marasmus,9
E42,0,E42,Marasmic kwashiorkor,Marasmic kwashiorkor,Marasmic kwashiorkor,9
E43,0,E43,Unspecified severe protein-calorie malnutrition,Unspecified severe protein-calorie malnutrition,Unspecified severe protein-calorie malnutrition,9
E45,0,E45,Retarded development following protein-calorie malnutrition,Retarded development following protein-calorie malnutrition,Retarded development following protein-calorie malnutrition,9
E46,0,E46,Unspecified protein-calorie malnutrition,Unspecified protein-calorie malnutrition,Unspecified protein-calorie malnutrition,9
E512,0,E512,Wernicke's encephalopathy,Wernicke's encephalopathy,Wernicke's encephalopathy,9
E518,0,E518,Other manifestations of thiamine deficiency,Other manifestations of thiamine deficiency,Other manifestations of thiamine deficiency,9
E519,0,E519,"Thiamine deficiency, unspecified","Thiamine deficiency, unspecified","Thiamine deficiency, unspecified",9
E52,0,E52,Niacin deficiency [pellagra],Niacin deficiency [pellagra],Niacin deficiency [pellagra],9
E54,0,E54,Ascorbic acid deficiency,Ascorbic acid deficiency,Ascorbic acid deficiency,9
E58,0,E58,Dietary calcium deficiency,Dietary calcium deficiency,Dietary calcium deficiency,9
E59,0,E59,Dietary selenium deficiency,Dietary selenium deficiency,Dietary selenium deficiency,9
E60,0,E60,Dietary zinc deficiency,Dietary zinc deficiency,Dietary zinc deficiency,9
E65,0,E65,Localized adiposity,Localized adiposity,Localized adiposity,9
E661,0,E661,Drug-induced obesity,Drug-induced obesity,Drug-induced obesity,9
E662,0,E662,Morbid (severe) obesity with alveolar hypoventilation,Morbid (severe) obesity with alveolar hypoventilation,Morbid (severe) obesity with alveolar hypoventilation,9
E663,0,E663,Overweight,Overweight,Overweight,9
E668,0,E668,Other obesity,Other obesity,Other obesity,9
E669,0,E669,"Obesity, unspecified","Obesity, unspecified","Obesity, unspecified",9
E68,0,E68,Sequelae of hyperalimentation,Sequelae of hyperalimentation,Sequelae of hyperalimentation,9
E7039,0,E7039,Other specified albinism,Other specified albinism,Other specified albinism,9
E705,0,E705,Disorders of tryptophan metabolism,Disorders of tryptophan metabolism,Disorders of tryptophan metabolism,9
E708,0,E708,Other disorders of aromatic amino-acid metabolism,Other disorders of aromatic amino-acid metabolism,Other disorders of aromatic amino-acid metabolism,9
E709,0,E709,"Disorder of aromatic amino-acid metabolism, unspecified","Disorder of aromatic amino-acid metabolism, unspecified","Disorder of aromatic amino-acid metabolism, unspecified",9
E7119,0,E7119,Other disorders of branched-chain amino-acid metabolism,Other disorders of branched-chain amino-acid metabolism,Other disorders of branched-chain amino-acid metabolism,9
E712,0,E712,"Disorder of branched-chain amino-acid metabolism, unsp","Disorder of branched-chain amino-acid metabolism, unspecified","Disorder of branched-chain amino-acid metabolism, unspecified",9
E7132,0,E7132,Disorders of ketone metabolism,Disorders of ketone metabolism,Disorders of ketone metabolism,9
E7139,0,E7139,Other disorders of fatty-acid metabolism,Other disorders of fatty-acid metabolism,Other disorders of fatty-acid metabolism,9
E7153,0,E7153,Other group 2 peroxisomal disorders,Other group 2 peroxisomal disorders,Other group 2 peroxisomal disorders,9
E723,0,E723,Disorders of lysine and hydroxylysine metabolism,Disorders of lysine and hydroxylysine metabolism,Disorders of lysine and hydroxylysine metabolism,9
E724,0,E724,Disorders of ornithine metabolism,Disorders of ornithine metabolism,Disorders of ornithine metabolism,9
E728,0,E728,Other specified disorders of amino-acid metabolism,Other specified disorders of amino-acid metabolism,Other specified disorders of amino-acid metabolism,9
E729,0,E729,"Disorder of amino-acid metabolism, unspecified","Disorder of amino-acid metabolism, unspecified","Disorder of amino-acid metabolism, unspecified",9
E744,0,E744,Disorders of pyruvate metabolism and gluconeogenesis,Disorders of pyruvate metabolism and gluconeogenesis,Disorders of pyruvate metabolism and gluconeogenesis,9
E748,0,E748,Other specified disorders of carbohydrate metabolism,Other specified disorders of carbohydrate metabolism,Other specified disorders of carbohydrate metabolism,9
E749,0,E749,"Disorder of carbohydrate metabolism, unspecified","Disorder of carbohydrate metabolism, unspecified","Disorder of carbohydrate metabolism, unspecified",9
E7525,0,E7525,Metachromatic leukodystrophy,Metachromatic leukodystrophy,Metachromatic leukodystrophy,9
E7529,0,E7529,Other sphingolipidosis,Other sphingolipidosis,Other sphingolipidosis,9
E753,0,E753,"Sphingolipidosis, unspecified","Sphingolipidosis, unspecified","Sphingolipidosis, unspecified",9
E754,0,E754,Neuronal ceroid lipofuscinosis,Neuronal ceroid lipofuscinosis,Neuronal ceroid lipofuscinosis,9
E755,0,E755,Other lipid storage disorders,Other lipid storage disorders,Other lipid storage disorders,9
E756,0,E756,"Lipid storage disorder, unspecified","Lipid storage disorder, unspecified","Lipid storage disorder, unspecified",9
E761,0,E761,"Mucopolysaccharidosis, type II","Mucopolysaccharidosis, type II","Mucopolysaccharidosis, type II",9
E7622,0,E7622,Sanfilippo mucopolysaccharidoses,Sanfilippo mucopolysaccharidoses,Sanfilippo mucopolysaccharidoses,9
E7629,0,E7629,Other mucopolysaccharidoses,Other mucopolysaccharidoses,Other mucopolysaccharidoses,9
E763,0,E763,"Mucopolysaccharidosis, unspecified","Mucopolysaccharidosis, unspecified","Mucopolysaccharidosis, unspecified",9
E768,0,E768,Other disorders of glucosaminoglycan metabolism,Other disorders of glucosaminoglycan metabolism,Other disorders of glucosaminoglycan metabolism,9
E769,0,E769,"Glucosaminoglycan metabolism disorder, unspecified","Glucosaminoglycan metabolism disorder, unspecified","Glucosaminoglycan metabolism disorder, unspecified",9
E781,0,E781,Pure hyperglyceridemia,Pure hyperglyceridemia,Pure hyperglyceridemia,9
E782,0,E782,Mixed hyperlipidemia,Mixed hyperlipidemia,Mixed hyperlipidemia,9
E783,0,E783,Hyperchylomicronemia,Hyperchylomicronemia,Hyperchylomicronemia,9
E784,0,E784,Other hyperlipidemia,Other hyperlipidemia,Other hyperlipidemia,9
E785,0,E785,"Hyperlipidemia, unspecified","Hyperlipidemia, unspecified","Hyperlipidemia, unspecified",9
E786,0,E786,Lipoprotein deficiency,Lipoprotein deficiency,Lipoprotein deficiency,9
E789,0,E789,"Disorder of lipoprotein metabolism, unspecified","Disorder of lipoprotein metabolism, unspecified","Disorder of lipoprotein metabolism, unspecified",9
E803,0,E803,Defects of catalase and peroxidase,Defects of catalase and peroxidase,Defects of catalase and peroxidase,9
E804,0,E804,Gilbert syndrome,Gilbert syndrome,Gilbert syndrome,9
E805,0,E805,Crigler-Najjar syndrome,Crigler-Najjar syndrome,Crigler-Najjar syndrome,9
E806,0,E806,Other disorders of bilirubin metabolism,Other disorders of bilirubin metabolism,Other disorders of bilirubin metabolism,9
F309,0,F309,"Manic episode, unspecified","Manic episode, unspecified","Manic episode, unspecified",9
E807,0,E807,"Disorder of bilirubin metabolism, unspecified","Disorder of bilirubin metabolism, unspecified","Disorder of bilirubin metabolism, unspecified",9
E8319,0,E8319,Other disorders of iron metabolism,Other disorders of iron metabolism,Other disorders of iron metabolism,9
E832,0,E832,Disorders of zinc metabolism,Disorders of zinc metabolism,Disorders of zinc metabolism,9
E839,0,E839,"Disorder of mineral metabolism, unspecified","Disorder of mineral metabolism, unspecified","Disorder of mineral metabolism, unspecified",9
E848,0,E848,Cystic fibrosis with other manifestations,Cystic fibrosis with other manifestations,Cystic fibrosis with other manifestations,9
E849,0,E849,"Cystic fibrosis, unspecified","Cystic fibrosis, unspecified","Cystic fibrosis, unspecified",9
E859,0,E859,"Amyloidosis, unspecified","Amyloidosis, unspecified","Amyloidosis, unspecified",9
E878,0,E878,"Oth disorders of electrolyte and fluid balance, NEC","Other disorders of electrolyte and fluid balance, not elsewhere classified","Other disorders of electrolyte and fluid balance, not elsewhere classified",9
E881,0,E881,"Lipodystrophy, not elsewhere classified","Lipodystrophy, not elsewhere classified","Lipodystrophy, not elsewhere classified",9
E882,0,E882,"Lipomatosis, not elsewhere classified","Lipomatosis, not elsewhere classified","Lipomatosis, not elsewhere classified",9
E883,0,E883,Tumor lysis syndrome,Tumor lysis syndrome,Tumor lysis syndrome,9
E889,0,E889,"Metabolic disorder, unspecified","Metabolic disorder, unspecified","Metabolic disorder, unspecified",9
E895,0,E895,Postprocedural testicular hypofunction,Postprocedural testicular hypofunction,Postprocedural testicular hypofunction,9
E896,0,E896,Postprocedural adrenocortical (-medullary) hypofunction,Postprocedural adrenocortical (-medullary) hypofunction,Postprocedural adrenocortical (-medullary) hypofunction,9
E8989,0,E8989,Oth postproc endocrine and metabolic comp and disorders,Other postprocedural endocrine and metabolic complications and disorders,Other postprocedural endocrine and metabolic complications and disorders,9
F04,0,F04,Amnestic disorder due to known physiological condition,Amnestic disorder due to known physiological condition,Amnestic disorder due to known physiological condition,9
F05,0,F05,Delirium due to known physiological condition,Delirium due to known physiological condition,Delirium due to known physiological condition,9
F064,0,F064,Anxiety disorder due to known physiological condition,Anxiety disorder due to known physiological condition,Anxiety disorder due to known physiological condition,9
F068,0,F068,Oth mental disorders due to known physiological condition,Other specified mental disorders due to known physiological condition,Other specified mental disorders due to known physiological condition,9
F079,0,F079,Unsp personality & behavrl disord due to known physiol cond,Unspecified personality and behavioral disorder due to known physiological condition,Unspecified personality and behavioral disorder due to known physiological condition,9
F09,0,F09,Unsp mental disorder due to known physiological condition,Unspecified mental disorder due to known physiological condition,Unspecified mental disorder due to known physiological condition,9
F1014,0,F1014,Alcohol abuse with alcohol-induced mood disorder,Alcohol abuse with alcohol-induced mood disorder,Alcohol abuse with alcohol-induced mood disorder,9
F1019,0,F1019,Alcohol abuse with unspecified alcohol-induced disorder,Alcohol abuse with unspecified alcohol-induced disorder,Alcohol abuse with unspecified alcohol-induced disorder,9
F1024,0,F1024,Alcohol dependence with alcohol-induced mood disorder,Alcohol dependence with alcohol-induced mood disorder,Alcohol dependence with alcohol-induced mood disorder,9
F1026,0,F1026,Alcohol depend w alcoh-induce persisting amnestic disorder,Alcohol dependence with alcohol-induced persisting amnestic disorder,Alcohol dependence with alcohol-induced persisting amnestic disorder,9
F1027,0,F1027,Alcohol dependence with alcohol-induced persisting dementia,Alcohol dependence with alcohol-induced persisting dementia,Alcohol dependence with alcohol-induced persisting dementia,9
F1029,0,F1029,Alcohol dependence with unspecified alcohol-induced disorder,Alcohol dependence with unspecified alcohol-induced disorder,Alcohol dependence with unspecified alcohol-induced disorder,9
F1094,0,F1094,"Alcohol use, unspecified with alcohol-induced mood disorder","Alcohol use, unspecified with alcohol-induced mood disorder","Alcohol use, unspecified with alcohol-induced mood disorder",9
F1096,0,F1096,"Alcohol use, unsp w alcoh-induce persist amnestic disorder","Alcohol use, unspecified with alcohol-induced persisting amnestic disorder","Alcohol use, unspecified with alcohol-induced persisting amnestic disorder",9
F1097,0,F1097,"Alcohol use, unsp with alcohol-induced persisting dementia","Alcohol use, unspecified with alcohol-induced persisting dementia","Alcohol use, unspecified with alcohol-induced persisting dementia",9
F1099,0,F1099,"Alcohol use, unsp with unspecified alcohol-induced disorder","Alcohol use, unspecified with unspecified alcohol-induced disorder","Alcohol use, unspecified with unspecified alcohol-induced disorder",9
F1114,0,F1114,Opioid abuse with opioid-induced mood disorder,Opioid abuse with opioid-induced mood disorder,Opioid abuse with opioid-induced mood disorder,9
F1119,0,F1119,Opioid abuse with unspecified opioid-induced disorder,Opioid abuse with unspecified opioid-induced disorder,Opioid abuse with unspecified opioid-induced disorder,9
F1123,0,F1123,Opioid dependence with withdrawal,Opioid dependence with withdrawal,Opioid dependence with withdrawal,9
F1124,0,F1124,Opioid dependence with opioid-induced mood disorder,Opioid dependence with opioid-induced mood disorder,Opioid dependence with opioid-induced mood disorder,9
F1129,0,F1129,Opioid dependence with unspecified opioid-induced disorder,Opioid dependence with unspecified opioid-induced disorder,Opioid dependence with unspecified opioid-induced disorder,9
F1193,0,F1193,"Opioid use, unspecified with withdrawal","Opioid use, unspecified with withdrawal","Opioid use, unspecified with withdrawal",9
F1194,0,F1194,"Opioid use, unspecified with opioid-induced mood disorder","Opioid use, unspecified with opioid-induced mood disorder","Opioid use, unspecified with opioid-induced mood disorder",9
F1199,0,F1199,"Opioid use, unsp with unspecified opioid-induced disorder","Opioid use, unspecified with unspecified opioid-induced disorder","Opioid use, unspecified with unspecified opioid-induced disorder",9
F1219,0,F1219,Cannabis abuse with unspecified cannabis-induced disorder,Cannabis abuse with unspecified cannabis-induced disorder,Cannabis abuse with unspecified cannabis-induced disorder,9
F1229,0,F1229,Cannabis dependence with unsp cannabis-induced disorder,Cannabis dependence with unspecified cannabis-induced disorder,Cannabis dependence with unspecified cannabis-induced disorder,9
F1299,0,F1299,"Cannabis use, unsp with unsp cannabis-induced disorder","Cannabis use, unspecified with unspecified cannabis-induced disorder","Cannabis use, unspecified with unspecified cannabis-induced disorder",9
F1314,0,F1314,"Sedative, hypnotic or anxiolytic abuse w mood disorder","Sedative, hypnotic or anxiolytic abuse with sedative, hypnotic or anxiolytic-induced mood disorder","Sedative, hypnotic or anxiolytic abuse with sedative, hypnotic or anxiolytic-induced mood disorder",9
F1319,0,F1319,"Sedative, hypnotic or anxiolytic abuse w unsp disorder","Sedative, hypnotic or anxiolytic abuse with unspecified sedative, hypnotic or anxiolytic-induced disorder","Sedative, hypnotic or anxiolytic abuse with unspecified sedative, hypnotic or anxiolytic-induced disorder",9
F1324,0,F1324,"Sedative, hypnotic or anxiolytic dependence w mood disorder","Sedative, hypnotic or anxiolytic dependence with sedative, hypnotic or anxiolytic-induced mood disorder","Sedative, hypnotic or anxiolytic dependence with sedative, hypnotic or anxiolytic-induced mood disorder",9
F1326,0,F1326,Sedatv/hyp/anxiolytc depend w persisting amnestic disorder,"Sedative, hypnotic or anxiolytic dependence with sedative, hypnotic or anxiolytic-induced persisting amnestic disorder","Sedative, hypnotic or anxiolytic dependence with sedative, hypnotic or anxiolytic-induced persisting amnestic disorder",9
F1327,0,F1327,Sedatv/hyp/anxiolytc dependence w persisting dementia,"Sedative, hypnotic or anxiolytic dependence with sedative, hypnotic or anxiolytic-induced persisting dementia","Sedative, hypnotic or anxiolytic dependence with sedative, hypnotic or anxiolytic-induced persisting dementia",9
F1329,0,F1329,"Sedative, hypnotic or anxiolytic dependence w unsp disorder","Sedative, hypnotic or anxiolytic dependence with unspecified sedative, hypnotic or anxiolytic-induced disorder","Sedative, hypnotic or anxiolytic dependence with unspecified sedative, hypnotic or anxiolytic-induced disorder",9
F1394,0,F1394,"Sedative, hypnotic or anxiolytic use, unsp w mood disorder","Sedative, hypnotic or anxiolytic use, unspecified with sedative, hypnotic or anxiolytic-induced mood disorder","Sedative, hypnotic or anxiolytic use, unspecified with sedative, hypnotic or anxiolytic-induced mood disorder",9
F1396,0,F1396,"Sedatv/hyp/anxiolytc use, unsp w persist amnestic disorder","Sedative, hypnotic or anxiolytic use, unspecified with sedative, hypnotic or anxiolytic-induced persisting amnestic disorder","Sedative, hypnotic or anxiolytic use, unspecified with sedative, hypnotic or anxiolytic-induced persisting amnestic disorder",9
F1397,0,F1397,"Sedatv/hyp/anxiolytc use, unsp w persisting dementia","Sedative, hypnotic or anxiolytic use, unspecified with sedative, hypnotic or anxiolytic-induced persisting dementia","Sedative, hypnotic or anxiolytic use, unspecified with sedative, hypnotic or anxiolytic-induced persisting dementia",9
F1399,0,F1399,"Sedative, hypnotic or anxiolytic use, unsp w unsp disorder","Sedative, hypnotic or anxiolytic use, unspecified with unspecified sedative, hypnotic or anxiolytic-induced disorder","Sedative, hypnotic or anxiolytic use, unspecified with unspecified sedative, hypnotic or anxiolytic-induced disorder",9
F1414,0,F1414,Cocaine abuse with cocaine-induced mood disorder,Cocaine abuse with cocaine-induced mood disorder,Cocaine abuse with cocaine-induced mood disorder,9
F1419,0,F1419,Cocaine abuse with unspecified cocaine-induced disorder,Cocaine abuse with unspecified cocaine-induced disorder,Cocaine abuse with unspecified cocaine-induced disorder,9
F1423,0,F1423,Cocaine dependence with withdrawal,Cocaine dependence with withdrawal,Cocaine dependence with withdrawal,9
F1424,0,F1424,Cocaine dependence with cocaine-induced mood disorder,Cocaine dependence with cocaine-induced mood disorder,Cocaine dependence with cocaine-induced mood disorder,9
F1429,0,F1429,Cocaine dependence with unspecified cocaine-induced disorder,Cocaine dependence with unspecified cocaine-induced disorder,Cocaine dependence with unspecified cocaine-induced disorder,9
F1494,0,F1494,"Cocaine use, unspecified with cocaine-induced mood disorder","Cocaine use, unspecified with cocaine-induced mood disorder","Cocaine use, unspecified with cocaine-induced mood disorder",9
F1499,0,F1499,"Cocaine use, unsp with unspecified cocaine-induced disorder","Cocaine use, unspecified with unspecified cocaine-induced disorder","Cocaine use, unspecified with unspecified cocaine-induced disorder",9
F1514,0,F1514,Other stimulant abuse with stimulant-induced mood disorder,Other stimulant abuse with stimulant-induced mood disorder,Other stimulant abuse with stimulant-induced mood disorder,9
F1519,0,F1519,Other stimulant abuse with unsp stimulant-induced disorder,Other stimulant abuse with unspecified stimulant-induced disorder,Other stimulant abuse with unspecified stimulant-induced disorder,9
F1523,0,F1523,Other stimulant dependence with withdrawal,Other stimulant dependence with withdrawal,Other stimulant dependence with withdrawal,9
F1524,0,F1524,Oth stimulant dependence w stimulant-induced mood disorder,Other stimulant dependence with stimulant-induced mood disorder,Other stimulant dependence with stimulant-induced mood disorder,9
F1529,0,F1529,Oth stimulant dependence w unsp stimulant-induced disorder,Other stimulant dependence with unspecified stimulant-induced disorder,Other stimulant dependence with unspecified stimulant-induced disorder,9
F1593,0,F1593,"Other stimulant use, unspecified with withdrawal","Other stimulant use, unspecified with withdrawal","Other stimulant use, unspecified with withdrawal",9
F1594,0,F1594,"Oth stimulant use, unsp with stimulant-induced mood disorder","Other stimulant use, unspecified with stimulant-induced mood disorder","Other stimulant use, unspecified with stimulant-induced mood disorder",9
F1599,0,F1599,"Oth stimulant use, unsp with unsp stimulant-induced disorder","Other stimulant use, unspecified with unspecified stimulant-induced disorder","Other stimulant use, unspecified with unspecified stimulant-induced disorder",9
F1614,0,F1614,Hallucinogen abuse with hallucinogen-induced mood disorder,Hallucinogen abuse with hallucinogen-induced mood disorder,Hallucinogen abuse with hallucinogen-induced mood disorder,9
F1619,0,F1619,Hallucinogen abuse with unsp hallucinogen-induced disorder,Hallucinogen abuse with unspecified hallucinogen-induced disorder,Hallucinogen abuse with unspecified hallucinogen-induced disorder,9
F1624,0,F1624,Hallucinogen dependence w hallucinogen-induced mood disorder,Hallucinogen dependence with hallucinogen-induced mood disorder,Hallucinogen dependence with hallucinogen-induced mood disorder,9
F1629,0,F1629,Hallucinogen dependence w unsp hallucinogen-induced disorder,Hallucinogen dependence with unspecified hallucinogen-induced disorder,Hallucinogen dependence with unspecified hallucinogen-induced disorder,9
F1694,0,F1694,"Hallucinogen use, unsp w hallucinogen-induced mood disorder","Hallucinogen use, unspecified with hallucinogen-induced mood disorder","Hallucinogen use, unspecified with hallucinogen-induced mood disorder",9
F1699,0,F1699,"Hallucinogen use, unsp w unsp hallucinogen-induced disorder","Hallucinogen use, unspecified with unspecified hallucinogen-induced disorder","Hallucinogen use, unspecified with unspecified hallucinogen-induced disorder",9
F1814,0,F1814,Inhalant abuse with inhalant-induced mood disorder,Inhalant abuse with inhalant-induced mood disorder,Inhalant abuse with inhalant-induced mood disorder,9
F1817,0,F1817,Inhalant abuse with inhalant-induced dementia,Inhalant abuse with inhalant-induced dementia,Inhalant abuse with inhalant-induced dementia,9
F1819,0,F1819,Inhalant abuse with unspecified inhalant-induced disorder,Inhalant abuse with unspecified inhalant-induced disorder,Inhalant abuse with unspecified inhalant-induced disorder,9
F1824,0,F1824,Inhalant dependence with inhalant-induced mood disorder,Inhalant dependence with inhalant-induced mood disorder,Inhalant dependence with inhalant-induced mood disorder,9
F1827,0,F1827,Inhalant dependence with inhalant-induced dementia,Inhalant dependence with inhalant-induced dementia,Inhalant dependence with inhalant-induced dementia,9
F1829,0,F1829,Inhalant dependence with unsp inhalant-induced disorder,Inhalant dependence with unspecified inhalant-induced disorder,Inhalant dependence with unspecified inhalant-induced disorder,9
F1894,0,F1894,"Inhalant use, unsp with inhalant-induced mood disorder","Inhalant use, unspecified with inhalant-induced mood disorder","Inhalant use, unspecified with inhalant-induced mood disorder",9
F1897,0,F1897,"Inhalant use, unsp with inhalant-induced persisting dementia","Inhalant use, unspecified with inhalant-induced persisting dementia","Inhalant use, unspecified with inhalant-induced persisting dementia",9
F1899,0,F1899,"Inhalant use, unsp with unsp inhalant-induced disorder","Inhalant use, unspecified with unspecified inhalant-induced disorder","Inhalant use, unspecified with unspecified inhalant-induced disorder",9
F1914,0,F1914,Oth psychoactive substance abuse w mood disorder,Other psychoactive substance abuse with psychoactive substance-induced mood disorder,Other psychoactive substance abuse with psychoactive substance-induced mood disorder,9
F1916,0,F1916,Oth psychoactv substance abuse w persist amnestic disorder,Other psychoactive substance abuse with psychoactive substance-induced persisting amnestic disorder,Other psychoactive substance abuse with psychoactive substance-induced persisting amnestic disorder,9
F1917,0,F1917,Oth psychoactive substance abuse w persisting dementia,Other psychoactive substance abuse with psychoactive substance-induced persisting dementia,Other psychoactive substance abuse with psychoactive substance-induced persisting dementia,9
F1919,0,F1919,Oth psychoactive substance abuse w unsp disorder,Other psychoactive substance abuse with unspecified psychoactive substance-induced disorder,Other psychoactive substance abuse with unspecified psychoactive substance-induced disorder,9
F1924,0,F1924,Oth psychoactive substance dependence w mood disorder,Other psychoactive substance dependence with psychoactive substance-induced mood disorder,Other psychoactive substance dependence with psychoactive substance-induced mood disorder,9
F1926,0,F1926,Oth psychoactv substance depend w persist amnestic disorder,Other psychoactive substance dependence with psychoactive substance-induced persisting amnestic disorder,Other psychoactive substance dependence with psychoactive substance-induced persisting amnestic disorder,9
F1927,0,F1927,Oth psychoactive substance dependence w persisting dementia,Other psychoactive substance dependence with psychoactive substance-induced persisting dementia,Other psychoactive substance dependence with psychoactive substance-induced persisting dementia,9
F1929,0,F1929,Oth psychoactive substance dependence w unsp disorder,Other psychoactive substance dependence with unspecified psychoactive substance-induced disorder,Other psychoactive substance dependence with unspecified psychoactive substance-induced disorder,9
F1994,0,F1994,"Oth psychoactive substance use, unsp w mood disorder","Other psychoactive substance use, unspecified with psychoactive substance-induced mood disorder","Other psychoactive substance use, unspecified with psychoactive substance-induced mood disorder",9
F1996,0,F1996,"Oth psychoactv sub use, unsp w persist amnestic disorder","Other psychoactive substance use, unspecified with psychoactive substance-induced persisting amnestic disorder","Other psychoactive substance use, unspecified with psychoactive substance-induced persisting amnestic disorder",9
F1997,0,F1997,"Oth psychoactive substance use, unsp w persisting dementia","Other psychoactive substance use, unspecified with psychoactive substance-induced persisting dementia","Other psychoactive substance use, unspecified with psychoactive substance-induced persisting dementia",9
F1999,0,F1999,"Oth psychoactive substance use, unsp w unsp disorder","Other psychoactive substance use, unspecified with unspecified psychoactive substance-induced disorder","Other psychoactive substance use, unspecified with unspecified psychoactive substance-induced disorder",9
F209,0,F209,"Schizophrenia, unspecified","Schizophrenia, unspecified","Schizophrenia, unspecified",9
F21,0,F21,Schizotypal disorder,Schizotypal disorder,Schizotypal disorder,9
F22,0,F22,Delusional disorders,Delusional disorders,Delusional disorders,9
F23,0,F23,Brief psychotic disorder,Brief psychotic disorder,Brief psychotic disorder,9
F24,0,F24,Shared psychotic disorder,Shared psychotic disorder,Shared psychotic disorder,9
F28,0,F28,Oth psych disorder not due to a sub or known physiol cond,Other psychotic disorder not due to a substance or known physiological condition,Other psychotic disorder not due to a substance or known physiological condition,9
F29,0,F29,Unsp psychosis not due to a substance or known physiol cond,Unspecified psychosis not due to a substance or known physiological condition,Unspecified psychosis not due to a substance or known physiological condition,9
F302,0,F302,"Manic episode, severe with psychotic symptoms","Manic episode, severe with psychotic symptoms","Manic episode, severe with psychotic symptoms",9
F303,0,F303,Manic episode in partial remission,Manic episode in partial remission,Manic episode in partial remission,9
F304,0,F304,Manic episode in full remission,Manic episode in full remission,Manic episode in full remission,9
F312,0,F312,"Bipolar disord, crnt episode manic severe w psych features","Bipolar disorder, current episode manic severe with psychotic features","Bipolar disorder, current episode manic severe with psychotic features",9
F314,0,F314,"Bipolar disord, crnt epsd depress, sev, w/o psych features","Bipolar disorder, current episode depressed, severe, without psychotic features","Bipolar disorder, current episode depressed, severe, without psychotic features",9
F315,0,F315,"Bipolar disord, crnt epsd depress, severe, w psych features","Bipolar disorder, current episode depressed, severe, with psychotic features","Bipolar disorder, current episode depressed, severe, with psychotic features",9
F319,0,F319,"Bipolar disorder, unspecified","Bipolar disorder, unspecified","Bipolar disorder, unspecified",9
F329,0,F329,"Major depressive disorder, single episode, unspecified","Major depressive disorder, single episode, unspecified","Major depressive disorder, single episode, unspecified",9
F338,0,F338,Other recurrent depressive disorders,Other recurrent depressive disorders,Other recurrent depressive disorders,9
F339,0,F339,"Major depressive disorder, recurrent, unspecified","Major depressive disorder, recurrent, unspecified","Major depressive disorder, recurrent, unspecified",9
F349,0,F349,"Persistent mood [affective] disorder, unspecified","Persistent mood [affective] disorder, unspecified","Persistent mood [affective] disorder, unspecified",9
F39,0,F39,Unspecified mood [affective] disorder,Unspecified mood [affective] disorder,Unspecified mood [affective] disorder,9
F408,0,F408,Other phobic anxiety disorders,Other phobic anxiety disorders,Other phobic anxiety disorders,9
F409,0,F409,"Phobic anxiety disorder, unspecified","Phobic anxiety disorder, unspecified","Phobic anxiety disorder, unspecified",9
F438,0,F438,Other reactions to severe stress,Other reactions to severe stress,Other reactions to severe stress,9
F439,0,F439,"Reaction to severe stress, unspecified","Reaction to severe stress, unspecified","Reaction to severe stress, unspecified",9
F449,0,F449,"Dissociative and conversion disorder, unspecified","Dissociative and conversion disorder, unspecified","Dissociative and conversion disorder, unspecified",9
F458,0,F458,Other somatoform disorders,Other somatoform disorders,Other somatoform disorders,9
F459,0,F459,"Somatoform disorder, unspecified","Somatoform disorder, unspecified","Somatoform disorder, unspecified",9
F502,0,F502,Bulimia nervosa,Bulimia nervosa,Bulimia nervosa,9
F509,0,F509,"Eating disorder, unspecified","Eating disorder, unspecified","Eating disorder, unspecified",9
F513,0,F513,Sleepwalking [somnambulism],Sleepwalking [somnambulism],Sleepwalking [somnambulism],9
F514,0,F514,Sleep terrors [night terrors],Sleep terrors [night terrors],Sleep terrors [night terrors],9
F515,0,F515,Nightmare disorder,Nightmare disorder,Nightmare disorder,9
F518,0,F518,Oth sleep disord not due to a sub or known physiol cond,Other sleep disorders not due to a substance or known physiological condition,Other sleep disorders not due to a substance or known physiological condition,9
F519,0,F519,"Sleep disorder not due to a sub or known physiol cond, unsp","Sleep disorder not due to a substance or known physiological condition, unspecified","Sleep disorder not due to a substance or known physiological condition, unspecified",9
F524,0,F524,Premature ejaculation,Premature ejaculation,Premature ejaculation,9
F525,0,F525,Vaginismus not due to a substance or known physiol condition,Vaginismus not due to a substance or known physiological condition,Vaginismus not due to a substance or known physiological condition,9
F526,0,F526,Dyspareunia not due to a substance or known physiol cond,Dyspareunia not due to a substance or known physiological condition,Dyspareunia not due to a substance or known physiological condition,9
F528,0,F528,Oth sexual dysfnct not due to a sub or known physiol cond,Other sexual dysfunction not due to a substance or known physiological condition,Other sexual dysfunction not due to a substance or known physiological condition,9
F529,0,F529,Unsp sexual dysfnct not due to a sub or known physiol cond,Unspecified sexual dysfunction not due to a substance or known physiological condition,Unspecified sexual dysfunction not due to a substance or known physiological condition,9
F53,0,F53,Puerperal psychosis,Puerperal psychosis,Puerperal psychosis,9
F54,0,F54,Psych & behavrl factors assoc w disord or dis classd elswhr,Psychological and behavioral factors associated with disorders or diseases classified elsewhere,Psychological and behavioral factors associated with disorders or diseases classified elsewhere,9
F59,0,F59,Unsp behavrl synd assoc w physiol disturb and physcl factors,Unspecified behavioral syndromes associated with physiological disturbances and physical factors,Unspecified behavioral syndromes associated with physiological disturbances and physical factors,9
F609,0,F609,"Personality disorder, unspecified","Personality disorder, unspecified","Personality disorder, unspecified",9
F639,0,F639,"Impulse disorder, unspecified","Impulse disorder, unspecified","Impulse disorder, unspecified",9
F659,0,F659,"Paraphilia, unspecified","Paraphilia, unspecified","Paraphilia, unspecified",9
F66,0,F66,Other sexual disorders,Other sexual disorders,Other sexual disorders,9
F688,0,F688,Other specified disorders of adult personality and behavior,Other specified disorders of adult personality and behavior,Other specified disorders of adult personality and behavior,9
F69,0,F69,Unspecified disorder of adult personality and behavior,Unspecified disorder of adult personality and behavior,Unspecified disorder of adult personality and behavior,9
F70,0,F70,Mild intellectual disabilities,Mild intellectual disabilities,Mild intellectual disabilities,9
F71,0,F71,Moderate intellectual disabilities,Moderate intellectual disabilities,Moderate intellectual disabilities,9
F72,0,F72,Severe intellectual disabilities,Severe intellectual disabilities,Severe intellectual disabilities,9
F73,0,F73,Profound intellectual disabilities,Profound intellectual disabilities,Profound intellectual disabilities,9
F78,0,F78,Other intellectual disabilities,Other intellectual disabilities,Other intellectual disabilities,9
F79,0,F79,Unspecified intellectual disabilities,Unspecified intellectual disabilities,Unspecified intellectual disabilities,9
F809,0,F809,"Developmental disorder of speech and language, unspecified","Developmental disorder of speech and language, unspecified","Developmental disorder of speech and language, unspecified",9
F819,0,F819,"Developmental disorder of scholastic skills, unspecified","Developmental disorder of scholastic skills, unspecified","Developmental disorder of scholastic skills, unspecified",9
F82,0,F82,Specific developmental disorder of motor function,Specific developmental disorder of motor function,Specific developmental disorder of motor function,9
F88,0,F88,Other disorders of psychological development,Other disorders of psychological development,Other disorders of psychological development,9
F89,0,F89,Unspecified disorder of psychological development,Unspecified disorder of psychological development,Unspecified disorder of psychological development,9
F983,0,F983,Pica of infancy and childhood,Pica of infancy and childhood,Pica of infancy and childhood,9
F984,0,F984,Stereotyped movement disorders,Stereotyped movement disorders,Stereotyped movement disorders,9
F985,0,F985,Adult onset fluency disorder,Adult onset fluency disorder,Adult onset fluency disorder,9
F988,0,F988,Oth behav/emotn disord w onset usly occur in chldhd and adol,Other specified behavioral and emotional disorders with onset usually occurring in childhood and adolescence,Other specified behavioral and emotional disorders with onset usually occurring in childhood and adolescence,9
F989,0,F989,Unsp behav/emotn disord w onst usly occur in chldhd and adol,Unspecified behavioral and emotional disorders with onset usually occurring in childhood and adolescence,Unspecified behavioral and emotional disorders with onset usually occurring in childhood and adolescence,9
F99,0,F99,"Mental disorder, not otherwise specified","Mental disorder, not otherwise specified","Mental disorder, not otherwise specified",9
G01,0,G01,Meningitis in bacterial diseases classified elsewhere,Meningitis in bacterial diseases classified elsewhere,Meningitis in bacterial diseases classified elsewhere,9
G02,0,G02,Meningitis in oth infec/parastc diseases classd elswhr,Meningitis in other infectious and parasitic diseases classified elsewhere,Meningitis in other infectious and parasitic diseases classified elsewhere,9
G041,0,G041,Tropical spastic paraplegia,Tropical spastic paraplegia,Tropical spastic paraplegia,9
G042,0,G042,"Bacterial meningoencephalitis and meningomyelitis, NEC","Bacterial meningoencephalitis and meningomyelitis, not elsewhere classified","Bacterial meningoencephalitis and meningomyelitis, not elsewhere classified",9
G07,0,G07,Intcrn & intraspinal abscs & granuloma in dis classd elswhr,Intracranial and intraspinal abscess and granuloma in diseases classified elsewhere,Intracranial and intraspinal abscess and granuloma in diseases classified elsewhere,9
G08,0,G08,Intracranial and intraspinal phlebitis and thrombophlebitis,Intracranial and intraspinal phlebitis and thrombophlebitis,Intracranial and intraspinal phlebitis and thrombophlebitis,9
G09,0,G09,Sequelae of inflammatory diseases of central nervous system,Sequelae of inflammatory diseases of central nervous system,Sequelae of inflammatory diseases of central nervous system,9
G10,0,G10,Huntington's disease,Huntington's disease,Huntington's disease,9
G128,0,G128,Other spinal muscular atrophies and related syndromes,Other spinal muscular atrophies and related syndromes,Other spinal muscular atrophies and related syndromes,9
G129,0,G129,"Spinal muscular atrophy, unspecified","Spinal muscular atrophy, unspecified","Spinal muscular atrophy, unspecified",9
G14,0,G14,Postpolio syndrome,Postpolio syndrome,Postpolio syndrome,9
G20,0,G20,Parkinson's disease,Parkinson's disease,Parkinson's disease,9
G212,0,G212,Secondary parkinsonism due to other external agents,Secondary parkinsonism due to other external agents,Secondary parkinsonism due to other external agents,9
G213,0,G213,Postencephalitic parkinsonism,Postencephalitic parkinsonism,Postencephalitic parkinsonism,9
G214,0,G214,Vascular parkinsonism,Vascular parkinsonism,Vascular parkinsonism,9
G218,0,G218,Other secondary parkinsonism,Other secondary parkinsonism,Other secondary parkinsonism,9
G219,0,G219,"Secondary parkinsonism, unspecified","Secondary parkinsonism, unspecified","Secondary parkinsonism, unspecified",9
G241,0,G241,Genetic torsion dystonia,Genetic torsion dystonia,Genetic torsion dystonia,9
G242,0,G242,Idiopathic nonfamilial dystonia,Idiopathic nonfamilial dystonia,Idiopathic nonfamilial dystonia,9
G243,0,G243,Spasmodic torticollis,Spasmodic torticollis,Spasmodic torticollis,9
G244,0,G244,Idiopathic orofacial dystonia,Idiopathic orofacial dystonia,Idiopathic orofacial dystonia,9
G245,0,G245,Blepharospasm,Blepharospasm,Blepharospasm,9
G248,0,G248,Other dystonia,Other dystonia,Other dystonia,9
G249,0,G249,"Dystonia, unspecified","Dystonia, unspecified","Dystonia, unspecified",9
G259,0,G259,"Extrapyramidal and movement disorder, unspecified","Extrapyramidal and movement disorder, unspecified","Extrapyramidal and movement disorder, unspecified",9
G26,0,G26,Extrapyramidal and movement disord in diseases classd elswhr,Extrapyramidal and movement disorders in diseases classified elsewhere,Extrapyramidal and movement disorders in diseases classified elsewhere,9
G311,0,G311,"Senile degeneration of brain, not elsewhere classified","Senile degeneration of brain, not elsewhere classified","Senile degeneration of brain, not elsewhere classified",9
G312,0,G312,Degeneration of nervous system due to alcohol,Degeneration of nervous system due to alcohol,Degeneration of nervous system due to alcohol,9
G319,0,G319,"Degenerative disease of nervous system, unspecified","Degenerative disease of nervous system, unspecified","Degenerative disease of nervous system, unspecified",9
G35,0,G35,Multiple sclerosis,Multiple sclerosis,Multiple sclerosis,9
G4089,0,G4089,Other seizures,Other seizures,Other seizures,9
G441,0,G441,"Vascular headache, not elsewhere classified","Vascular headache, not elsewhere classified","Vascular headache, not elsewhere classified",9
G478,0,G478,Other sleep disorders,Other sleep disorders,Other sleep disorders,9
G479,0,G479,"Sleep disorder, unspecified","Sleep disorder, unspecified","Sleep disorder, unspecified",9
G53,0,G53,Cranial nerve disorders in diseases classified elsewhere,Cranial nerve disorders in diseases classified elsewhere,Cranial nerve disorders in diseases classified elsewhere,9
G55,0,G55,Nerve root and plexus compressions in diseases classd elswhr,Nerve root and plexus compressions in diseases classified elsewhere,Nerve root and plexus compressions in diseases classified elsewhere,9"""  
    array = []

    lists = f.splitlines()
    for line in lists: 
        # array = []
        PATTERN = re.compile(r'''((?:[^,"']|"[^"]*"|'[^']*')+)''')
        lineCol = PATTERN.split(line)[1::2]
        # lineCol =  re.split(r',"?!"?:[^"]*\"[^"]*\""*[^""]*\""', line)
        # array.append(lineCol[6])
        if ((len(lineCol) == 7) and lineCol[6] == "9"):
            icdcode = {}
            icdcode['categoryCode'] = lineCol[0]
            icdcode['diagnosisCode'] = lineCol[1]
            icdcode['fullCode'] = lineCol[2]
            icdcode['abbrDesc'] = lineCol[3]
            icdcode['fullDesc'] = lineCol[4]
            icdcode['categoryTitle'] = lineCol[5]

            # array.append(icdcode)

            serializer = ICDCodeSerializer(data=icdcode)
            if serializer.is_valid():
                serializer.save()

            # array.append(icdcode)
            # icdcode.appVersion = int(line[6])
            # icdcode.save()  

    # f.close()  
    f = ""
    response_format = {}
    response_format["status"] = 'success'
    response_format["message"] = 'Done'
    response_format["data"] = array
    return Response(response_format)
