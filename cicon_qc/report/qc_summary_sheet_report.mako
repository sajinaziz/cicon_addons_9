<htm>
    <head>
       <style type="text/css">
        ${css}

        td.header
        {
            font-weight: bold;
            width:15%;
        }

        td.with_border
        {
            border:1px solid ;

        }
        td.with_border_bottom
        {
            border:1px darkgrey;
        }

        th
        {
            border:1px solid;

        }

        table
        {
            width: 100%;


        }
        table.with_border
        {
            width: 100%;
            border:1px solid;
            border-collapse: collapse;
        }

       </style>
    </head>
    <body>

            <table class="with_border">
                <caption style="text-align: center">Delivery Summary Details </caption>
                <thead>
                    <th> Trip Ref. </th>
                    <th> Customer</th>
                    <th> Project</th>
                    <th> Date</th>
                    <th> Delivery Notes</th>
                    <th> Certificates</th>
                </thead>

                <tbody>
                % for qc_sheet in objects:
                    <tr>
                        <td class="with_border" style="width:7% "> ${qc_sheet.name}</td>
                        <td class="with_border" style="width:15%"> ${qc_sheet.partner_id.name}</td>
                        <td class="with_border"  style="width:20%"> ${qc_sheet.project_id.name}</td>
                        <td class="with_border"  style="width:8%"> ${qc_sheet.delivery_date}</td>
                        <td class="with_border" style="width:20%">
                            <table>
                            % for dn in qc_sheet.dn_line_ids:
                                <tr>
                                    <td class="with_border_bottom" style="width:20%;"> ${dn.dn_no}</td>
                                    <td class="with_border_bottom">
                                    % for c in dn.order_code_ids:
                                        ${c.name}
                                        %if not loop.last:
                                                ,
                                        %endif
                                    %endfor
                                    </td>
                                </tr>
                            %endfor
                            </table>
                        </td>
                        <td class="with_border" style="width:30%">
                            <table>
                                %for mill in qc_sheet.certificate_line_ids:
                                    <tr>
                                        <td>
                                            ${mill.dia_attrib_value_id.name}
                                        </td>
                                        <td>
                                            ${mill.origin_attrib_value_id.name}
                                        </td>
                                        <td>
                                             % for cert in mill.certificate_ids:
                                                 ${cert.name}
                                                  %if not loop.last:
                                                        ,
                                                  %endif
                                             %endfor
                                        </td>
                                    </tr>
                                %endfor
                            </table>
                        </td>
                    </tr>
                %endfor
                </tbody>

            </table>


    </body>
</htm>