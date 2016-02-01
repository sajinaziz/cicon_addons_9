<!doctype html>
<html>
<head>
    <style type="text/css">
        ${css}



    table
    {
        font-size: 16;
        font-family: tahoma;
        width: 100%;
        margin: 2px;
        border: 1px solid;
        border-collapse:collapse ;
    }


     td
    {
       border:1px solid #808080;
       height: 35px;
        padding: 3px;
     }
    table.normal th
    {
        border: 1px solid;
        height: 32px;
    }
    caption
    {
        font-weight: bold;
        height: 35px;
        font-size: 20;
        border: 1px solid;
        text-align: center;
    }
     table.with_th th
     {
         border-left: 1px solid;
         border-right: 1px solid;
         height: 25px;
     }

     div.label
      {
         display: inline-block;
         float: left;
         width:25% ;
       }
      p.small_note
	{
		font-size: 14;
	        font-family: tahoma;

	}




    </style>
##
##    <script src="http://code.jquery.com/jquery-1.10.1.min.js"></script>
##    <link rel="stylesheet" href="http://netdna.bootstrapcdn.com/bootstrap/3.1.0/css/bootstrap.min.css"/>
##    <script src="http://netdna.bootstrapcdn.com/bootstrap/3.1.0/js/bootstrap.min.js"></script>

</head>

<body>
% for order in objects:

##<p class="text-center">
##    Hi
##</p>
##
##
##<small>How this is happened</small>
##
##<table class="table table-bordered">
##    <thead>
##        <th>Col1 </th>
##        <th>Col2 </th>
##        <th>Col3 </th>
##    </thead>
##    <tbody>
##        <tr>
##            <td>1</td>
##            <td>2</td>
##            <td>3</td>
##        </tr>
##    </tbody>
##</table>

<table class="normal">
    <caption style="font-size:22;font-weight: bolder;height:40px;">
        Customer's Requisition Form</caption>
    <thead>
        <tr>
            <th style="width: 51%">To be filled by Technical Dept.</th>

            <th style="width: 49%">To be filled by Production Dept.</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td>
                <div class="label"> Client Name:</div>
                <div >  ${order.partner_id.name} </div>
            </td>

            <td>
                <div class="label" style="width:40%;"> Order Received By: </div>
             </td>
        </tr>
        <tr>
            <td>
                <div class="label"> Project Name:</div>
                <div >  ${order.project_id.name} </div>
             </td>
            <td>
                <div class="label" style="width:40%;"> Order Received On:</div>
                <div>  ${formatLang(order.received_datetime,date_time=True )} </div>
             </td>
        </tr>
        <tr>
            <td>
                <div class="label"  style="width:30%"> Order Ref #:</div>
                <div class="label" style="font-weight: bold;width:40%">  ${order.name} </div>
	   <div class="label" style="width:10%"> Pages: </div>
	  <div class="label" style="width:20%"> ${order.page_info or ' '} </div>


            </td>
            <td>Schedule Checked : (Yes/ No) </td>
        </tr>
        <tr>
            <td>
                <div class="label"> List Details:</div>
                <div>  ${order.title} </div>

            </td>
            <td>Printed Sch / Tags : (Yes/ No) </td>
        </tr>
        <tr>
            <td>
             <div class="label"> Sub List:</div>
             <div>  ${order.subtitle or ''} </div></td>
            <td>Attach Mill Certificates : (Yes/ No) </td>
        </tr>
        <tr>
            <td>
             <div class="label"> Type of Steel:</div>
             <div>  ${order.material_type or ''} </div>
            </td>
            <td>BBS For : (Item / Sample / STB) </td>
        </tr>
         <tr>
            <td>
               <div class="label" style="width:20%;">Order Date:</div>
               <div class="label" style="width:30%;">  ${formatLang(order.order_date,date=True)}  </div>
               <div class="label" style="width:15%;">Req.Date: </div>
               <div class="label" style="width:35%;">  ${formatLang(order.required_date,date=True)}  </div>
            </td>
            <td>BBS Incl Coupler : (Yes / No) </td>
        </tr>
        <tr>
            <td>
                <div class="label"> Eng. Name:</div>
                <div>  ${order.project_engineer or order.created_by.name}</div>
           </td>
            <td>
                Prod. Material Status: (Ready / Not Ready)
            </td>

        </tr>

        <tr>
            <td>Eng. Signature</td>
            <td></td>
        </tr>
    </tbody>
    <tfoot>
        <tr>
            <td style="height:100px;vertical-align:top"> Notes From Technical If Any :-
                <p> ${order.technical_note or ''}  </p>
            </td>
            <td style="height:100px;vertical-align:top">Notes From Production If Any :-
                    <p> ${order.production_note or ''}  </p>
            </td>
        </tr>
    </tfoot>

</table>


<table class="with_th">
    <caption>Job Work Status/ Account Details</caption>
    <thead>
        <tr>
            <th style="width: 15%" />
            <th style="width: 10%"/>
            <th colspan="6" style="border-bottom:1px solid;width:50% ; " >Total Number of Thread bars</th>
            <th></th>
            <th></th>
            <th></th>
        </tr>
        <tr>
        <th> File Code</th>
        <th> Thread Type</th>
            <th> 12 mm </th>
          <th> 16 mm </th>
                   <th> 20 mm </th>
                   <th> 25 mm </th>
                   <th> 32 mm </th>
                   <th> 40 mm </th>
        <th> Weight (Tons)</th>
        <th> Delivery Note No:</th>
        <th> Delivery Date :</th>
        </tr>

    </thead>

    <tbody>
       %for a in range(1,15,1):
           <tr>
               <td></td>
               <td></td>
               <td></td>
               <td></td>
               <td></td>
               <td></td>
               <td></td>
               <td></td>
               <td></td>
               <td></td>
               <td></td>
           </tr>
       %endfor
    </tbody>
</table>
<p class="small_note">
     <div style="font-size:10px;float: right;"> ${formatLang(time.strftime('%Y-%m-%d %H:%M:%S'), date_time=True)}</div>
</p>
%endfor
</body>

</html>