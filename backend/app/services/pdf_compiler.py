import subprocess
import os
import tempfile
import shutil
import logging
from typing import Tuple

logger = logging.getLogger("pdf_compiler")

class PDFCompiler:
    @staticmethod
    def is_xelatex_installed() -> bool:
        return shutil.which("xelatex") is not None

    @classmethod
    async def compile_tex(cls, tex_content: str, timeout_seconds: int = 30) -> bytes:
        """
        Compiles the LaTeX source string to PDF using XeLaTeX in a subprocess.
        Returns the raw PDF bytes.
        """
        if not cls.is_xelatex_installed():
            logger.warning("xelatex is not installed on the system. Generating a fallback mock PDF.")
            # Generate a minimal mock PDF file or raise an error in production
            # We return dummy PDF bytes for local development runnability
            return cls._generate_mock_pdf()

        # Write tex file to temp directory
        with tempfile.TemporaryDirectory() as temp_dir:
            tex_file_path = os.path.join(temp_dir, "resume.tex")
            pdf_file_path = os.path.join(temp_dir, "resume.pdf")

            with open(tex_file_path, "w", encoding="utf-8") as f:
                f.write(tex_content)

            cmd = [
                "xelatex",
                "-interaction=nonstopmode",
                f"-output-directory={temp_dir}",
                tex_file_path
            ]

            try:
                # Run the compiler
                # Run twice for cross-references to compile properly
                for run_idx in range(2):
                    result = subprocess.run(
                        cmd,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        timeout=timeout_seconds,
                        text=True
                    )
                    
                    if result.returncode != 0:
                        logger.error(f"XeLaTeX failed on run {run_idx+1}.\nStdout: {result.stdout}\nStderr: {result.stderr}")
                        raise RuntimeError(
                            f"XeLaTeX compilation failed with exit code {result.returncode}.\n"
                            f"LaTeX Log Summary:\n{result.stdout[-1000:]}"
                        )
                
                # Read output PDF
                if not os.path.exists(pdf_file_path):
                    raise FileNotFoundError("XeLaTeX compiled successfully but no output PDF was created.")
                
                with open(pdf_file_path, "rb") as f:
                    pdf_bytes = f.read()

                return pdf_bytes

            except subprocess.TimeoutExpired as e:
                logger.error(f"XeLaTeX execution timed out: {e}")
                raise TimeoutError("XeLaTeX compilation timed out. Check for recursive macros or invalid loops.")
            except Exception as e:
                logger.error(f"LaTeX compile error: {e}")
                raise

    @staticmethod
    def _generate_mock_pdf() -> bytes:
        # Minimal valid PDF content bytes
        return b"%PDF-1.4\n1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n3 0 obj\n<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R >>\nendobj\n4 0 obj\n<< /Length 44 >>\nstream\nBT /F1 24 Tf 100 700 Td (AI Optimized Resume) Tj ET\nendstream\nendobj\nxref\n0 5\n0000000000 65535 f\n0000000009 00000 n\n0000000058 00000 n\n0000000115 00000 n\n0000000212 00000 n\ntrailer\n<< /Size 5 /Root 1 0 R >>\nstartxref\n307\n%%EOF\n"
