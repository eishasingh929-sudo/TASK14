import { VerificationStatus } from "../types/uniguru";

interface Props {
  status?: VerificationStatus;
  domain?: string;
}

export function VerificationBadge({ status = "UNVERIFIED", domain }: Props) {
  const cls = status === "VERIFIED" ? "verified" : status === "PARTIAL" ? "partial" : "unverified";
  return (
    <span className={`badge ${cls}`}>
      {status}
      {domain ? ` | ${domain}` : ""}
    </span>
  );
}
