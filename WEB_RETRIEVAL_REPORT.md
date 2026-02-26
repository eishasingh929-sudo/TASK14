# UniGuru Verified Web Retrieval Report

## 🌐 Live Intelligence Layer
The Web Retrieval system allows UniGuru to access live information while maintaining strict governance and verification standards.

## 🛡️ Verification Gate
Unlike traditional search, UniGuru verifies every domain and content snippet against a `SourceVerifier`.

### Tiered Classification
- **VERIFIED**: Official archives, academic sites, government portals (.edu, .gov, specific domains).
- **PARTIAL**: News organizations, established encyclopedias (Wikipedia, Reuters).
- **UNVERIFIED**: Blogs, social media, unverified news. **(REFUSED)**.

## ⚙️ Retrieval Pipeline
1. **Query Trigger**: Engine detects KB gap.
2. **Web Search**: Consults allowed domain list.
3. **Retrieval**: Fetches raw content.
4. **Verification**: `SourceVerifier` audits the source.
5. **Enforcement**: If `UNVERIFIED`, system **refuses** to answer.

## 🧪 Search Validation Test
**Query**: "Tell me about the oldest Jain text."
**Action**: Web Search -> Wikipedia/Sacred-Texts.
**Result**: `VERIFIED` -> Answer Returned with Source URL.

## 🚫 Refusal Execution
- **Query**: "What is the latest unverified rumor about X?"
- **Action**: Web Search -> Blogspot.com.
- **Result**: `UNVERIFIED` -> System Refusal: "I cannot verify this information."
