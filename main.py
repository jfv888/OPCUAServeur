import asyncio
from asyncua import Server, ua
import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(21, GPIO.OUT)
GPIO.setup(20, GPIO.OUT)
GPIO.setup(16, GPIO.OUT)

async def main():
    serveur = Server()
    await serveur.init()
    serveur.set_server_name("OPC UA SERVER RGB")

    url = "opc.tcp://10.4.1.219:4840"

    serveur.set_endpoint(url)
    serveur.set_security_policy([ua.SecurityPolicyType.NoSecurity,
                                 ua.SecurityPolicyType.Basic256Sha256_SignAndEncrypt,
                                 ua.SecurityPolicyType.Basic256Sha256_Sign])

    nom = "OPC_UA_SERVEUR_RGB"
    espace_adresse = await serveur.register_namespace(nom)

    LED1 = await serveur.nodes.objects.add_object(espace_adresse, "LED1")
    noeud_variable_rouge = await LED1.add_variable(espace_adresse, "rouge", False)
    noeud_variable_vert = await LED1.add_variable(espace_adresse, "vert", False)
    noeud_variable_bleu = await LED1.add_variable(espace_adresse, "bleu", False)

    await noeud_variable_rouge.set_writable(True)
    await noeud_variable_vert.set_writable(True)
    await noeud_variable_bleu.set_writable(True)


    async def Fermer(parent):
        print("Mise en marche du moteur")
        await noeud_variable_rouge.set_value(False)
        await noeud_variable_vert.set_value(False)
        await noeud_variable_bleu.set_value(False)

    noeud_methode_fermer = await LED1.add_method(espace_adresse, "FermerLed", Fermer, [], [ua.VariantType.Boolean])

    async with serveur:
        while True:
            if await noeud_variable_rouge.get_value():
                GPIO.output(16, 0)
            else:
                GPIO.output(16, 1)
            if await noeud_variable_vert.get_value():
                GPIO.output(20, 0)
            else:
                GPIO.output(20, 1)
            if await noeud_variable_bleu.get_value():
                GPIO.output(21, 0)
            else:
                GPIO.output(21, 1)
            await asyncio.sleep(1)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Fin")
        GPIO.cleanup()