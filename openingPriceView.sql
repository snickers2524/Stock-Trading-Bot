SELECT op.date,
       op.open,
       op1.open as op1,
       op2.open as op2,
       op3.open as op3,
       op4.open as op4,
       op5.open as op5,
       op6.open as op6,
       op7.open as op7,
       op8.open as op8,
       op9.open as op9,
       op1.open as op10
FROM (SELECT ROW_NUMBER() OVER (ORDER BY date) AS rowNum, date, open FROM openingPrices) AS op
    JOIN (SELECT ROW_NUMBER() OVER (ORDER BY date) AS rowNum, date, open FROM openingPrices) as op1 on op.rowNum = op1.rowNum + 1
JOIN (SELECT ROW_NUMBER() OVER (ORDER BY date) AS rowNum, date, open FROM openingPrices) as op2 on op.rowNum = op2.rowNum + 2
JOIN (SELECT ROW_NUMBER() OVER (ORDER BY date) AS rowNum, date, open FROM openingPrices) as op3 on op.rowNum = op3.rowNum + 3
JOIN (SELECT ROW_NUMBER() OVER (ORDER BY date) AS rowNum, date, open FROM openingPrices) as op4 on op.rowNum = op4.rowNum + 4
JOIN (SELECT ROW_NUMBER() OVER (ORDER BY date) AS rowNum, date, open FROM openingPrices) as op5 on op.rowNum = op5.rowNum + 5
JOIN (SELECT ROW_NUMBER() OVER (ORDER BY date) AS rowNum, date, open FROM openingPrices) as op6 on op.rowNum = op6.rowNum + 6
JOIN (SELECT ROW_NUMBER() OVER (ORDER BY date) AS rowNum, date, open FROM openingPrices) as op7 on op.rowNum = op7.rowNum + 7
JOIN (SELECT ROW_NUMBER() OVER (ORDER BY date) AS rowNum, date, open FROM openingPrices) as op8 on op.rowNum = op8.rowNum + 8
JOIN (SELECT ROW_NUMBER() OVER (ORDER BY date) AS rowNum, date, open FROM openingPrices) as op9 on op.rowNum = op9.rowNum + 9
JOIN (SELECT ROW_NUMBER() OVER (ORDER BY date) AS rowNum, date, open FROM openingPrices) as op10 on op.rowNum = op10.rowNum + 10


select * from openingPrices;
