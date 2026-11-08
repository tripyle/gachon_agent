import pandas as pd
from io import BytesIO
from openpyxl.utils import get_column_letter


def create_excel_file(
    grading_df,
    summary,
    question_df,
    most_wrong
):
    output = BytesIO()

    with pd.ExcelWriter(output, engine="openpyxl") as writer:

        sheet_name = "시험 성적 분석"

        # 1. 전체 성적 개요
        summary_title = pd.DataFrame(
            [["전체 성적 개요"]],
            columns=["항목"]
        )

        summary_title.to_excel(
            writer,
            sheet_name=sheet_name,
            index=False,
            header=False,
            startrow=0
        )

        summary_df = pd.DataFrame(
            list(summary.items()),
            columns=["항목", "결과"]
        )

        summary_df.to_excel(
            writer,
            sheet_name=sheet_name,
            index=False,
            startrow=2
        )

        # 2. 가장 많이 틀린 문항 TOP 3
        most_wrong_title_row = len(summary_df) + 4

        pd.DataFrame(
            [["가장 많이 틀린 문항 TOP 3"]],
            columns=["항목"]
        ).to_excel(
            writer,
            sheet_name=sheet_name,
            index=False,
            header=False,
            startrow=most_wrong_title_row
        )

        most_wrong.to_excel(
            writer,
            sheet_name=sheet_name,
            index=False,
            startrow=most_wrong_title_row + 2
        )

        # 3. 학생별 채점 결과
        student_title_row = (
            most_wrong_title_row + len(most_wrong) + 4
        )

        pd.DataFrame(
            [["학생별 채점 결과"]],
            columns=["항목"]
        ).to_excel(
            writer,
            sheet_name=sheet_name,
            index=False,
            header=False,
            startrow=student_title_row
        )

        grading_df.to_excel(
            writer,
            sheet_name=sheet_name,
            index=False,
            startrow=student_title_row + 2
        )

        # 4. 열 너비 자동 조정
        worksheet = writer.sheets[sheet_name]

        for column_cells in worksheet.columns:
            max_length = 0
            column_letter = get_column_letter(
                column_cells[0].column
            )

            for cell in column_cells:
                if cell.value is not None:
                    max_length = max(
                        max_length,
                        len(str(cell.value))
                    )

            worksheet.column_dimensions[
                column_letter
            ].width = min(max_length + 3, 30)

        # 5. 제목 행 굵게 표시
        from openpyxl.styles import Font

        for row in [1, 2 + len(summary_df) + 2, student_title_row + 1]:
            worksheet.cell(row=row, column=1).font = Font(
                bold=True,
                size=12
            )

    output.seek(0)
    return output
