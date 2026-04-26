import { buildModule } from "@nomicfoundation/hardhat-ignition/modules";

const ThresholdAttestorModule = buildModule("ThresholdAttestorModule", (m) => {
  const initialOwner = m.getParameter("initialOwner");

  const signedAttestationVerifier = m.contract("SignedAttestationVerifierV25", [initialOwner]);
  const thresholdNetworkAdapter = m.contract("ThresholdNetworkAdapterV25", [initialOwner, signedAttestationVerifier]);

  return { signedAttestationVerifier, thresholdNetworkAdapter };
});

export default ThresholdAttestorModule;
